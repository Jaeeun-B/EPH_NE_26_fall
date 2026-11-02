"""손목 카메라(C09) 장착 위치 탐색: 실제로 달 수 있는 위치 중 C09 선량이 가장 작은 곳 (궤적 고정).

배경
- 14의 민감도(공구 축 방향으로 10, 20 cm 뒤)는 좌표만 옮긴 값이라 장착 가능성을 보지 않았다.
- A6 관절축은 A7 링크 좌표 z 약 -0.08 m에 있다. 20 cm 뒤(z = -0.1 m)는 그보다 뒤라 손목이 꺾이면 로봇 몸체와 겹친다.
- 그래서 장착 제약을 넣고 다시 찾는다. 궤적(B0, P3)은 그대로 두고 카메라 위치만 바꾼다.

후보: A4~A7 링크(pybullet 링크 3~6)에 고정한 점. 링크 좌표계 각 축 -0.25~0.25 m, 2.5 cm 간격
제약 (값은 모두 가정, 아래 상수)
1) 카메라 머리(반지름 2.5 cm 구)가 장착 링크 외의 로봇 링크, 공구, 운반 중인 베드와 겹치지 않음 (작업 전체)
2) 장착 링크 표면에서 12 cm 이내 (브래킷 길이)이고 표면 안쪽으로 1 cm보다 깊지 않음.
   A7 링크에 달 때는 공구 표면도 장착면으로 본다
3) 환경·벽과 2 cm(로봇과 같은 d_safe), 베드와 0.5 cm 이상 떨어짐 (작업 전체)
4) S2 커플링 해제, S5 커플링 체결 체류 자세에서 공구 끝 외곽(반지름 5 cm 원 위 8점) 중 3점 이상이
   직선으로 보이고, TCP까지 0.5 m 이내
목적: 작업 전체 C09 누적선량 (가상 선원 상대값) 최소

실행: python scripts/15_camera_placement.py        (06, 13을 먼저 실행)
출력: outputs/camera/ placement.json (최적 위치, 탈락 이유, 제약 가정 민감도), candidates_<tag>.csv
"""
import csv
import json
import time

import numpy as np
import pybullet as p

import _bootstrap  # noqa: F401
from datraj import OUTPUTS
from datraj.components import load as load_components
from datraj.dose_eval import build_fields
from datraj.scene import Scene
from datraj.task import apply_state, task_steps

CAM_R = 0.025          # 카메라 머리 반지름 [m] (가정)
BRACKET = 0.12         # 장착면에서 카메라 표면까지 최대 거리 [m] (가정)
EMBED = 0.01           # 장착면에 파묻혀도 되는 깊이 [m]. 현재 위치(공구 옆면)가 공구 표면에 0.5 cm 걸쳐 있음
BED_MARGIN = 0.005     # 베드와 최소 거리 [m]
RING_R = 0.05          # 확인할 공구 끝 외곽 원 반지름 [m] (공구 반지름 0.04 m + 1 cm)
RING_N = 8
MIN_VISIBLE = 3        # 8점 중 보여야 하는 점 수 (135° 호)
MAX_VIEW = 0.5         # 카메라-TCP 최대 거리 [m] (해상도 가정)
GRID = np.round(np.arange(-0.25, 0.25001, 0.025), 4)
MOUNT_LINKS = {3: "A4 링크", 4: "A5 링크", 5: "A6 링크", 6: "A7 링크·공구"}
STRIDE = 10            # 작업 전체 충돌 검사에서 궤적 행 간격 (구간 경계와 체류는 항상 포함)
CHUNK = 300
SENS = [(0.5, 0.12, 3), (0.4, 0.12, 3), (0.3, 0.12, 3), (0.5, 0.06, 3), (0.5, 0.12, 5)]  # 민감도 조합
MAX_TRY = 3000         # 링크마다 선량이 작은 순으로 제약을 확인할 최대 후보 수


def load_traj(tag):
    with open(OUTPUTS / tag / f"traj_{tag}.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    t = np.array([float(r["t"]) for r in rows])
    seg = np.array([int(r["segment"]) for r in rows])
    q = np.array([[float(r[f"q_A{j}"]) for j in range(1, 8)] for r in rows])
    return t, seg, q


class Placement:
    def __init__(self, scene, tag, max_view=MAX_VIEW, bracket=BRACKET, min_visible=MIN_VISIBLE):
        self.scene, self.tag = scene, tag
        self.max_view, self.bracket, self.min_visible = max_view, bracket, min_visible
        self.steps = task_steps()
        self.t, self.seg, self.q = load_traj(tag)
        r = scene.robot
        T = len(self.q)
        self.pos = np.zeros((T, 7, 3))
        self.R = np.zeros((T, 7, 3, 3))
        for i, qi in enumerate(self.q):
            self.pos[i], self.R[i] = r.link_frames(qi)
        self.tcp = self.pos[:, 6] + np.einsum("tij,j->ti", self.R[:, 6], r.tcp_local)
        self.fields = build_fields("model")
        self.seg_idx = []
        for s in range(self.seg.max() + 1):
            idx = np.nonzero(self.seg == s)[0]
            if s > 0:
                idx = np.concatenate([[idx[0] - 1], idx])
            self.seg_idx.append(idx)
        # 충돌 검사용 표본: STRIDE 간격 + 구간 경계 + 체류 첫 행
        keep = set(range(0, T, STRIDE)) | {int(i[0]) for i in self.seg_idx} | {int(i[-1]) for i in self.seg_idx}
        self.check_rows = np.array(sorted(keep))
        self.dwell_rows = {self.steps[s].dwell_key: int(np.nonzero(self.seg == s)[0][0])
                           for s in range(len(self.steps)) if self.steps[s].kind == "dwell"}
        cs = p.createCollisionShape(p.GEOM_SPHERE, radius=CAM_R, physicsClientId=scene.cid)
        self.cam = p.createMultiBody(0, cs, -1, [0, 0, -10], physicsClientId=scene.cid)

    # ----------------------------------------------------------- 선량
    def c09_dose(self, link, offs, S=1.0):
        """offs (K, 3) 후보들의 작업 전체 C09 누적선량 [Gy] (가상 선원)."""
        offs = np.atleast_2d(offs)
        out = np.zeros(len(offs))
        for a in range(0, len(offs), CHUNK):
            o = offs[a:a + CHUNK]
            P = self.pos[:, link][:, None, :] + np.einsum("tij,kj->tki", self.R[:, link], o)
            for s, idx in enumerate(self.seg_idx):
                f = self.fields[self.steps[s].field]
                r = f.rate(P[idx], self.tcp[idx], self.R[idx, 6], self.t[idx]) * S
                out[a:a + CHUNK] += np.trapezoid(r, self.t[idx], axis=0) / 3600.0
        return out

    # ----------------------------------------------------------- 기하
    def world(self, row, link, off):
        return self.pos[row, link] + self.R[row, link] @ np.asarray(off, float)

    def _set(self, row):
        sc = self.scene
        s = int(self.seg[row])
        apply_state(sc, self.steps[s].state)
        sc.robot.link_frames(self.q[row])
        sc.update_attached(self.q[row])

    def _place(self, x):
        p.resetBasePositionAndOrientation(self.cam, list(map(float, x)), [0, 0, 0, 1],
                                          physicsClientId=self.scene.cid)

    def _robot_contact(self, link, margin=0.0):
        """장착 링크(A7이면 공구 포함)를 뺀 로봇 링크·공구와 margin 이내면 그 이름, 아니면 ''."""
        sc = self.scene
        for c in p.getClosestPoints(self.cam, sc.robot.id, margin, physicsClientId=sc.cid):
            if c[4] != link:
                return f"로봇 링크{c[4]}"
        if link != 6 and p.getClosestPoints(self.cam, sc.tool_body, margin, physicsClientId=sc.cid):
            return "공구"
        return ""

    def local_ok(self, row, link, off):
        """기준 자세에서 몸체 바깥(1)과 브래킷 길이(2) 확인. 실패 이유 문자열 또는 ''.

        장착면(장착 링크, A7이면 공구 포함)에는 붙어 있어야 하므로 EMBED까지 파묻히는 것은 허용한다.
        카메라 기준점이 장착면 안쪽으로 그보다 깊으면 몸체 안으로 본다.
        """
        sc = self.scene
        self._set(row)
        self._place(self.world(row, link, off))
        other = self._robot_contact(link)
        if other:
            return f"{other}와 겹침"
        d = [c[8] for c in p.getClosestPoints(self.cam, sc.robot.id, self.bracket, linkIndexB=link,
                                              physicsClientId=sc.cid)]
        if link == 6:
            d += [c[8] for c in p.getClosestPoints(self.cam, sc.tool_body, self.bracket, physicsClientId=sc.cid)]
        if not d:
            return "장착면에서 너무 멂"
        if min(d) < -EMBED:
            return "장착 링크 몸체 안"
        return ""

    def view_ok(self, link, off):
        """체류 자세(S2, S5)에서 공구 끝 외곽이 보이는지. (통과 여부, 이유, 보인 점 수 목록)"""
        sc = self.scene
        self._place([0, 0, -10])
        phi = np.linspace(0, 2 * np.pi, RING_N, endpoint=False)
        ring = np.stack([RING_R * np.cos(phi), RING_R * np.sin(phi),
                         np.full(RING_N, sc.robot.tcp_local[2])], axis=1)
        seen = []
        for key in ("S2_dwell", "S5_dwell"):
            row = self.dwell_rows[key]
            self._set(row)
            c = self.world(row, link, off)
            if np.linalg.norm(c - self.tcp[row]) > self.max_view:
                return False, f"{key} TCP까지 {self.max_view} m 초과", seen
            tg = self.pos[row, 6] + ring @ self.R[row, 6].T
            hits = p.rayTestBatch([c.tolist()] * RING_N, tg.tolist(), physicsClientId=sc.cid)
            vis = sum(1 for h, x in zip(hits, tg) if h[0] < 0 or np.linalg.norm(np.asarray(h[3]) - x) < 0.01)
            seen.append(vis)
            if vis < self.min_visible:
                return False, f"{key} 공구 끝 외곽 {vis}/{RING_N}점만 보임", seen
        return True, "", seen

    def path_ok(self, link, off):
        """작업 전체에서 로봇·공구·운반 베드(1), 환경·벽·베드(3) 충돌 확인."""
        sc = self.scene
        m_env = sc.margin
        for row in self.check_rows:
            self._set(row)
            self._place(self.world(row, link, off))
            other = self._robot_contact(link)
            if other:
                return False, f"t = {self.t[row]:.1f} s {other}와 겹침"
            if p.getClosestPoints(self.cam, sc.env, m_env, physicsClientId=sc.cid):
                return False, f"t = {self.t[row]:.1f} s 환경과 {m_env} m 이내"
            for wb, _, _ in sc.walls:
                if p.getClosestPoints(self.cam, wb, m_env, physicsClientId=sc.cid):
                    return False, f"t = {self.t[row]:.1f} s 벽과 {m_env} m 이내"
            for which, body in sc.bodies.items():
                if sc.bed_state.get(which) == "hidden":
                    continue
                if p.getClosestPoints(self.cam, body, BED_MARGIN, physicsClientId=sc.cid):
                    return False, f"t = {self.t[row]:.1f} s 베드({which})와 {BED_MARGIN} m 이내"
        return True, ""

    def check(self, link, off):
        ref = self.dwell_rows["S2_dwell"]
        why = self.local_ok(ref, link, off)
        if why:
            return False, why, []
        ok, why, seen = self.view_ok(link, off)
        if not ok:
            return False, why, seen
        ok, why = self.path_ok(link, off)
        return ok, why, seen


def reason_kind(why):
    if not why:
        return "통과"
    if why.startswith("t ="):
        return "작업 중 충돌"
    if "초과" in why:
        return "시야 거리"
    if "보임" in why:
        return "시야 가림"
    return "장착 불가"


def search(pl, comps, d_default, verbose=True):
    k09 = next(k for k, c in enumerate(comps) if c.id == "C09")
    S = comps[k09].S
    ref = pl.dwell_rows["S2_dwell"]
    grid = np.array([[x, y, z] for x in GRID for y in GRID for z in GRID])
    cands = []
    for L in MOUNT_LINKS:
        ok = [o for o in grid if not pl.local_ok(ref, L, o)]
        d = pl.c09_dose(L, np.array(ok), S)
        cands += [(float(di), L, o) for di, o in zip(d, ok)]
        if verbose:
            print(f"  {MOUNT_LINKS[L]}: 격자 {len(grid)}점 중 몸체 바깥·브래킷 범위 {len(ok)}점")
    cands.sort(key=lambda c: c[0])
    best, tried, n_try = {}, [], {L: 0 for L in MOUNT_LINKS}
    kinds = {}
    for d, L, o in cands:
        if L in best or n_try[L] >= MAX_TRY:
            continue
        n_try[L] += 1
        ok, why, seen = pl.check(L, o)
        kinds[reason_kind(why)] = kinds.get(reason_kind(why), 0) + 1
        tried.append({"link": L, "offset": [float(v) for v in o], "C09_Gy": d,
                      "change_pct": (d / d_default - 1) * 100, "ok": ok, "reason": why, "visible": seen})
        if ok:
            best[L] = tried[-1]
            if verbose:
                print(f"  {MOUNT_LINKS[L]} 최적: 오프셋 {np.round(o, 3)} m, C09 {(d / d_default - 1) * 100:+.1f}% "
                      f"(이 링크에서 선량이 더 작은 후보 {n_try[L] - 1}개 탈락)")
        if len(best) + sum(1 for L in MOUNT_LINKS if L not in best and n_try[L] >= MAX_TRY) == len(MOUNT_LINKS):
            break
    for L in MOUNT_LINKS:
        if L not in best and verbose:
            print(f"  {MOUNT_LINKS[L]}: 선량이 작은 후보 {n_try[L]}개 모두 제약 불통과")
    return cands, best, tried, kinds


def describe(pl, link, off):
    """체류 자세에서 카메라-TCP 거리, 작업 전체 환경·베드 최소 거리 [m]."""
    sc = pl.scene
    view = {}
    for key in ("S2_dwell", "S5_dwell"):
        row = pl.dwell_rows[key]
        view[key] = float(np.linalg.norm(pl.world(row, link, off) - pl.tcp[row]))
    dmin = 1.0
    for row in pl.check_rows:
        pl._set(row)
        pl._place(pl.world(row, link, off))
        for body in [sc.env] + [wb for wb, _, _ in sc.walls] + [b for w, b in sc.bodies.items()
                                                              if sc.bed_state.get(w) != "hidden"]:
            for c in p.getClosestPoints(pl.cam, body, 1.0, physicsClientId=sc.cid):
                dmin = min(dmin, c[8])
    return {"cam_to_tcp_m": view, "min_clearance_env_bed_m": float(dmin)}


def main():
    scene = Scene()
    comps, _ = load_components()
    k09 = next(k for k, c in enumerate(comps) if c.id == "C09")
    base = comps[k09]
    out = OUTPUTS / "camera"
    out.mkdir(parents=True, exist_ok=True)
    result = {
        "note": "가상 선원 상대값. 궤적 고정, C09 위치만 바꿈. 제약 값은 모두 가정",
        "constraints": {"camera_radius_m": CAM_R, "bracket_m": BRACKET, "env_margin_m": scene.margin,
                        "bed_margin_m": BED_MARGIN, "ring_radius_m": RING_R, "ring_points": RING_N,
                        "min_visible": MIN_VISIBLE, "max_view_m": MAX_VIEW,
                        "grid_m": [float(GRID[0]), float(GRID[-1]), 0.025],
                        "mount_links": {str(k): v for k, v in MOUNT_LINKS.items()}},
        "default": {"link": base.link, "offset": [float(v) for v in base.offset]},
    }
    for tag in ("b0", "p3"):
        if not (OUTPUTS / tag / f"traj_{tag}.csv").exists():
            print(f"outputs/{tag}가 없어 건너뜀")
            continue
        t0 = time.time()
        print(f"[{tag}] 궤적 {tag.upper()}에서 카메라 위치 탐색")
        pl = Placement(scene, tag)
        d0 = float(pl.c09_dose(base.link, base.offset, base.S)[0])
        ok0, why0, seen0 = pl.check(base.link, base.offset)
        print(f"  현재 위치 {base.offset} (A7 링크): 제약 {'통과' if ok0 else '불통과 ' + why0}, 보인 점 {seen0}")
        old = []
        for dz in (0.10, 0.20):
            o = np.asarray(base.offset, float) - np.array([0, 0, dz])
            ok, why, seen = pl.check(base.link, o)
            d = float(pl.c09_dose(base.link, o, base.S)[0])
            old.append({"shift_m": dz, "offset": [float(v) for v in o], "C09_Gy": d,
                        "change_pct": (d / d0 - 1) * 100, "ok": ok, "reason": why})
            print(f"  14 민감도 {dz:.2f} m 뒤: C09 {(d / d0 - 1) * 100:+.1f}%, 제약 {'통과' if ok else '불통과 (' + why + ')'}")
        cands, best, tried, kinds = search(pl, comps, d0)
        for b in best.values():
            b.update(describe(pl, b["link"], b["offset"]))
        with open(out / f"candidates_{tag}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["link", "x_m", "y_m", "z_m", "C09_Gy", "change_pct"])
            for d, L, o in cands:
                w.writerow([L, *[f"{v:.3f}" for v in o], f"{d:.6e}", f"{(d / d0 - 1) * 100:.2f}"])
        overall = min(best.values(), key=lambda b: b["C09_Gy"]) if best else None
        result[tag] = {
            "default_C09_Gy": d0, "default_ok": ok0, "default_reason": why0, "default_visible": seen0,
            "shift_check": old,
            "n_candidates": len(cands),
            "best_by_link": {MOUNT_LINKS[L]: b for L, b in sorted(best.items())},
            "best": overall,
            "n_tried": len(tried),
            "reject_kinds": kinds,
            "tried_head": tried[:40],
            "elapsed_s": round(time.time() - t0, 1),
        }
        if overall:
            print(f"  전체 최적: {MOUNT_LINKS[overall['link']]} 오프셋 {overall['offset']} m, "
                  f"C09 {overall['change_pct']:+.1f}% ({time.time() - t0:.0f} s)")
    # 제약 가정 민감도 (B0 궤적): 시야 거리, 브래킷 길이, 보여야 하는 점 수
    if "b0" in result:
        sens = []
        d0 = result["b0"]["default_C09_Gy"]
        for mv, br, mvis in SENS:
            pl = Placement(scene, "b0", max_view=mv, bracket=br, min_visible=mvis)
            _, best, _, _ = search(pl, comps, d0, verbose=False)
            b = min(best.values(), key=lambda x: x["C09_Gy"]) if best else None
            sens.append({"max_view_m": mv, "bracket_m": br, "min_visible": mvis,
                         "best_link": MOUNT_LINKS[b["link"]] if b else None,
                         "best_offset": b["offset"] if b else None,
                         "C09_change_pct": b["change_pct"] if b else None,
                         "A7_tool_change_pct": best[6]["change_pct"] if 6 in best else None})
            print(f"  민감도 시야 {mv} m, 브래킷 {br} m, 보일 점 {mvis}: "
                  + (f"{sens[-1]['best_link']} C09 {b['change_pct']:+.1f}%" if b else "가능한 위치 없음")
                  + (f", A7·공구만 쓰면 {best[6]['change_pct']:+.1f}%" if 6 in best else ", A7·공구 가능 위치 없음"))
        result["sensitivity_b0"] = sens
    with open(out / "placement.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(f"출력 폴더: {out}")


if __name__ == "__main__":
    main()
