"""선량장과 부품 단위 누적선량 평가기.

D_k = S_k * ∫ Ḋ(p_k(q(t)), t) dt   (Ḋ: Gy/h, t: s, D: Gy)
- 정적 구간: 선량 격자(3선형 보간) 또는 선원 해석식
- S3 반출 구간: 로봇이 든 베드 선원을 TCP 자세로 옮겨 매 시점 계산 (dose_model)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import GRID_DIR, config
from .components import Component
from .dose_grid import DoseGrid
from .dose_model import Source, dose_rate, sources_from_dicts
from .geometry import rot_x


class DoseField:
    name = "field"

    def rate(self, P: np.ndarray, tcp_pos: np.ndarray, tcp_R: np.ndarray, t: np.ndarray) -> np.ndarray:
        """P: (T, K, 3) -> (T, K) Gy/h"""
        raise NotImplementedError


class GridField(DoseField):
    def __init__(self, grid: DoseGrid):
        self.grid = grid
        self.name = f"grid:{grid.meta.get('grid_id')}"

    def rate(self, P, tcp_pos, tcp_R, t):
        return self.grid(P, warn_outside=False)


class SourceField(DoseField):
    def __init__(self, sources: list[Source], name="sources"):
        self.sources = sources
        self.name = name

    def rate(self, P, tcp_pos, tcp_R, t):
        return dose_rate(P, self.sources)


class AttachedSourceField(DoseField):
    """로봇이 든 베드의 선원. 원래 자리(베드 축이 연직)에서 정의된 선원을 TCP 자세로 옮긴다."""

    def __init__(self, sources: list[Source], home_center, bed_offset_from_tcp: float, name="carried"):
        self.sources = sources
        self.home_center = np.asarray(home_center, float)
        self.off = float(bed_offset_from_tcp)
        self.name = name

    def rate(self, P, tcp_pos, tcp_R, t):
        out = np.zeros(P.shape[:2])
        for i in range(P.shape[0]):
            center = tcp_pos[i] + tcp_R[i][:, 2] * self.off
            Rb = tcp_R[i] @ rot_x(np.pi)
            moved = [s.transformed(Rb, center - Rb @ self.home_center) for s in self.sources]
            out[i] = dose_rate(P[i], moved)
        return out


class SumField(DoseField):
    def __init__(self, fields: list[DoseField]):
        self.fields = fields
        self.name = " + ".join(f.name for f in fields)

    def rate(self, P, tcp_pos, tcp_R, t):
        return sum(f.rate(P, tcp_pos, tcp_R, t) for f in self.fields)


def build_fields(mode: str = "model", N: int = 100, grid_dir=None) -> dict[str, DoseField]:
    """구간별 선량장.

    mode = "model": 가상 선원 해석식 (격자 보간 오차 없음)
    mode = "grid" : data/dose_grids 의 격자 (방사선 파트 격자로 교체하는 경로)
    반환 키: pre (Bed A 있음), post (Bed A 제거), carry_spent (post + 들고 가는 Bed A)
    """
    layout = config.layout()
    bed = layout["bed_cartridge"]
    off = bed["handle_height"] + bed["height"] / 2
    home = layout["task_sites"]["bed_A_center"]
    if mode == "grid":
        gdir = grid_dir or GRID_DIR
        pre = DoseGrid.load(gdir / f"dose_grid_pre_N{N}.npy") if N else DoseGrid.load(gdir / "dose_grid_pre.npy")
        post = DoseGrid.load(gdir / f"dose_grid_post_N{N}.npy") if N else DoseGrid.load(gdir / "dose_grid_post.npy")
        bedA = [s for s in pre.meta["sources"] if s["id"] == "bed_A"]
        if not bedA:
            raise ValueError("pre 격자 메타데이터에 id='bed_A' 선원이 없습니다 (S3 이동 선원 계산에 필요)")
        f_pre, f_post = GridField(pre), GridField(post)
        carried = sources_from_dicts(bedA, pre.meta.get("r_min", 0.05))
    else:
        vs = config.virtual_sources()
        by_id = {s["id"]: s for s in vs["sources"]}
        mk = lambda ids: sources_from_dicts([by_id[i] for i in ids], vs["r_min"])  # noqa: E731
        f_pre = SourceField(mk(vs["states"]["pre_removal"]), "model:pre")
        f_post = SourceField(mk(vs["states"]["post_removal"]), "model:post")
        carried = mk(["bed_A"])
    return {
        "pre": f_pre,
        "post": f_post,
        "carry_spent": SumField([f_post, AttachedSourceField(carried, home, off, "carried:bed_A")]),
    }


@dataclass
class DoseResult:
    rates: np.ndarray   # (T, K) Gy/h, 차폐 투과율 적용
    dose: np.ndarray    # (K,) Gy


class ComponentDoseEvaluator:
    def __init__(self, robot, components: list[Component]):
        self.robot = robot
        self.comps = components
        self.links = np.array([c.link for c in components])
        self.offsets = np.array([c.offset for c in components])
        self.S = np.array([c.S for c in components])

    def positions(self, qs: np.ndarray):
        """(T, K, 3) 부품 위치, (T, 3) TCP 위치, (T, 3, 3) TCP 회전."""
        qs = np.atleast_2d(qs)
        T, K = len(qs), len(self.comps)
        P = np.zeros((T, K, 3))
        tcp = np.zeros((T, 3))
        Rt = np.zeros((T, 3, 3))
        base_pts = self.robot.base_pos + self.offsets @ self.robot.base_R.T
        for i, q in enumerate(qs):
            pos, R = self.robot.link_frames(q)
            for k in range(K):
                L = self.links[k]
                P[i, k] = base_pts[k] if L < 0 else pos[L] + R[L] @ self.offsets[k]
            tcp[i] = pos[6] + R[6] @ self.robot.tcp_local
            Rt[i] = R[6]
        return P, tcp, Rt

    def evaluate(self, ts: np.ndarray, qs: np.ndarray, field: DoseField) -> DoseResult:
        P, tcp, Rt = self.positions(qs)
        rates = field.rate(P, tcp, Rt, ts) * self.S[None, :]
        if len(ts) < 2:
            return DoseResult(rates, np.zeros(len(self.comps)))
        dose = np.trapezoid(rates, ts, axis=0) / 3600.0
        return DoseResult(rates, dose)
