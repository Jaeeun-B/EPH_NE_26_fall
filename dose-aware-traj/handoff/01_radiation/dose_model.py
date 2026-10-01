"""선량률 함수 인터페이스 (방사선 파트 <-> 경로계획 파트)

경로계획 코드는 이 파일의 dose_rate(points, sources, t)만 호출한다.
방사선 파트는 함수 이름과 인자, 반환 형식을 유지한 채 내부 계산만 바꾸면 된다.

규약
- 좌표: hotcell_layout.json의 hotcell_world 좌표계, 단위 m
- 반환: 흡수선량률 Gy/h (dose_grid_meta.json의 medium과 같은 매질 기준)
- points: (..., 3) 배열. 반환은 (...) 배열
- sources: Source 목록. 이동 선원(S3에서 로봇이 들고 가는 베드)은 호출하는 쪽에서
  Source.transformed(R, p)로 위치를 옮긴 뒤 넘긴다.
- t: 작업 시작 후 경과 시간 (s). 현재 참조 구현은 붕괴를 무시하므로 쓰지 않는다.

참조 구현
- point: D(r) = S / max(r, r_min)^2
- line: 균일 선선원, 1/r^2 커널을 선분을 따라 해석적으로 적분
      D = (S / L) / d * [atan((L - s) / d) + atan(s / d)],  d = max(수직거리, r_min)
- polyline: 선분별로 길이에 비례해 세기를 나눈 line의 합
- strength S: 해당 선원 전체를 1 m 거리의 점선원으로 봤을 때의 선량률 (Gy/h at 1 m)

필요한 패키지: numpy
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Iterable, Sequence

import numpy as np

INTERFACE_VERSION = "1.0"
DEFAULT_R_MIN = 0.05


@dataclass
class Source:
    id: str
    kind: str                      # "point" | "line" | "polyline"
    strength: float                # Gy/h at 1 m (선원 전체)
    points: np.ndarray = field(default_factory=lambda: np.zeros((1, 3)))
    r_min: float = DEFAULT_R_MIN   # 선원 반경. 이보다 가까운 거리는 r_min으로 본다
    note: str = ""

    def __post_init__(self):
        self.points = np.atleast_2d(np.asarray(self.points, dtype=float))
        need = {"point": 1, "line": 2}
        if self.kind in need and self.points.shape[0] != need[self.kind]:
            raise ValueError(f"{self.id}: {self.kind} 선원은 점 {need[self.kind]}개가 필요합니다")
        if self.kind == "polyline" and self.points.shape[0] < 2:
            raise ValueError(f"{self.id}: polyline 선원은 점 2개 이상이 필요합니다")
        if self.strength < 0:
            raise ValueError(f"{self.id}: strength는 0 이상이어야 합니다")

    def transformed(self, R: np.ndarray, p: np.ndarray) -> "Source":
        """강체 변환 x' = R x + p 를 적용한 선원 (이동 선원용)."""
        pts = self.points @ np.asarray(R).T + np.asarray(p)
        return replace(self, points=pts)

    def to_dict(self) -> dict:
        d = {"id": self.id, "kind": self.kind, "strength": float(self.strength),
             "r_min": float(self.r_min)}
        if self.kind == "point":
            d["position"] = self.points[0].tolist()
        elif self.kind == "line":
            d["start"], d["end"] = self.points[0].tolist(), self.points[1].tolist()
        else:
            d["points"] = self.points.tolist()
        if self.note:
            d["note"] = self.note
        return d


def source_from_dict(d: dict, r_min: float = DEFAULT_R_MIN) -> Source:
    kind = d["kind"]
    if kind == "point":
        pts = [d["position"]]
    elif kind == "line":
        pts = [d["start"], d["end"]]
    elif kind == "polyline":
        pts = d["points"]
    else:
        raise ValueError(f"지원하지 않는 선원 종류: {kind}")
    return Source(id=d["id"], kind=kind, strength=float(d["strength"]), points=pts,
                  r_min=float(d.get("r_min", r_min)), note=d.get("note", ""))


def sources_from_dicts(items: Iterable[dict], r_min: float = DEFAULT_R_MIN) -> list[Source]:
    return [source_from_dict(d, r_min) for d in items]


def sources_from_meta(meta: dict) -> list[Source]:
    """dose_grid_meta.json의 sources 항목을 Source 목록으로 변환."""
    return sources_from_dicts(meta.get("sources", []), meta.get("r_min", DEFAULT_R_MIN))


# ---------------------------------------------------------------------------
# 커널
# ---------------------------------------------------------------------------

def _point_kernel(P: np.ndarray, pos: np.ndarray, S: float, r_min: float) -> np.ndarray:
    r2 = np.sum((P - pos) ** 2, axis=-1)
    return S / np.maximum(r2, r_min ** 2)


def _line_kernel(P: np.ndarray, a: np.ndarray, b: np.ndarray, S: float, r_min: float) -> np.ndarray:
    ab = b - a
    L = float(np.linalg.norm(ab))
    if L < 1e-9:
        return _point_kernel(P, a, S, r_min)
    u = ab / L
    ap = P - a
    s = ap @ u                                   # 선분 시작점 기준 축방향 좌표
    perp = ap - s[..., None] * u
    d = np.maximum(np.linalg.norm(perp, axis=-1), r_min)
    return (S / L) / d * (np.arctan((L - s) / d) + np.arctan(s / d))


def dose_rate(points, sources: Sequence[Source], t: float | None = None) -> np.ndarray:
    """선량률 (Gy/h).

    points  : (..., 3) 위치 [m]
    sources : Source 목록
    t       : 경과 시간 [s]. 참조 구현에서는 사용하지 않음
    """
    P = np.asarray(points, dtype=float)
    out = np.zeros(P.shape[:-1])
    for src in sources:
        if src.strength == 0:
            continue
        if src.kind == "point":
            out += _point_kernel(P, src.points[0], src.strength, src.r_min)
        elif src.kind == "line":
            out += _line_kernel(P, src.points[0], src.points[1], src.strength, src.r_min)
        elif src.kind == "polyline":
            seg = np.diff(src.points, axis=0)
            lens = np.linalg.norm(seg, axis=1)
            total = lens.sum()
            for a, b, l in zip(src.points[:-1], src.points[1:], lens):
                out += _line_kernel(P, a, b, src.strength * l / total, src.r_min)
        else:
            raise ValueError(f"지원하지 않는 선원 종류: {src.kind}")
    return out


def grid_from_sources(sources: Sequence[Source], origin, spacing, shape,
                      t: float | None = None, chunk: int = 200_000) -> np.ndarray:
    """격자 노드에서 dose_rate를 계산한 배열 (axis_order = xyz, 노드 기준)."""
    axes = [origin[i] + spacing[i] * np.arange(shape[i]) for i in range(3)]
    X, Y, Z = np.meshgrid(*axes, indexing="ij")
    pts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=-1)
    vals = np.empty(len(pts))
    for i in range(0, len(pts), chunk):
        vals[i:i + chunk] = dose_rate(pts[i:i + chunk], sources, t)
    return vals.reshape(shape)


if __name__ == "__main__":
    # 간단한 자기 점검
    src = Source("p", "point", 1.0, [[0, 0, 0]])
    assert np.isclose(dose_rate([[2.0, 0, 0]], [src])[0], 0.25)
    ln = Source("l", "line", 1.0, [[0, 0, -50], [0, 0, 50]])
    # 선선원 중앙 옆 1 m: (S/L)/d * 2*atan(L/2d)
    val = dose_rate([[1.0, 0, 0]], [ln])[0]
    assert np.isclose(val, (1.0 / 100.0) * 2 * np.arctan(50.0), rtol=1e-9)
    far = Source("l2", "line", 1.0, [[0, 0, -0.01], [0, 0, 0.01]])
    assert np.isclose(dose_rate([[3.0, 0, 0]], [far])[0], 1.0 / 9.0, rtol=1e-4)
    print("dose_model self-check OK (interface", INTERFACE_VERSION + ")")
