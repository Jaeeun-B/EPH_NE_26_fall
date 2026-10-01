"""B1: 엔드이펙터(TCP) 3D A* (선량 가중 격자) + IK 추종.

이동로봇 연구에서 쓰는 '점 로봇' 가정을 매니퓰레이터에 그대로 옮긴 비교 기준이다.
- 비용: 구간 길이 x (TCP 위치 선량률 + w_time). 팔의 다른 부품 선량은 보지 않는다.
- 점유: 공구(와 운반 중인 베드)를 TCP 기준 선분으로 근사해 배치도 도형과의 거리로 판정
- 도달 가능 영역: 손목 중심과 어깨 사이 거리로 근사. 실제 가능 여부는 IK 추종에서 확인
"""
from __future__ import annotations

import heapq
import itertools

import numpy as np

from .geometry import dist_point_object, rot_z, tool_down_R
from .layout_plot import objects_for_state
from .planning import edge_free

STATE_FOR_LAYOUT = {"pre_removal": "pre_removal", "carry_spent": "post_removal_nocask",
                    "post_removal": "post_removal", "carry_new": "post_removal_nonew", "installed": "installed"}


def _obstacles(layout, state):
    base = state
    if state == "carry_spent":
        objs = [o for o in objects_for_state(layout, "post_removal") if o["id"] != "spent_bed(cask)"]
    elif state == "carry_new":
        objs = [o for o in objects_for_state(layout, "post_removal") if o["id"] != "new_bed"]
    else:
        objs = objects_for_state(layout, base)
    walls = [o for o in layout["objects"] if o["id"].startswith("wall") or o["id"] == "floor"]
    return objs + walls


class EEGrid:
    def __init__(self, scene, res: float = 0.04, lo=(-0.6, -0.9, 0.08), hi=(1.0, 0.9, 1.2)):
        self.scene = scene
        self.res = res
        self.lo = np.asarray(lo, float)
        self.shape = tuple(int(np.floor((h - l) / res)) + 1 for l, h in zip(lo, hi))
        ax = [self.lo[i] + res * np.arange(self.shape[i]) for i in range(3)]
        X, Y, Z = np.meshgrid(*ax, indexing="ij")
        self.P = np.stack([X, Y, Z], axis=-1)
        self.reach = self._reachable()
        self._occ_cache = {}

    def _reachable(self):
        """공구를 아래로 향한 채 TCP가 갈 수 있는 칸.

        A3 = A5 = 0 평면 팔(A2 어깨, A4 팔꿈치, A6 손목)로 근사한다. 손목 중심(A6)이 어깨에서 닿는 거리 안에 있고,
        공구를 아래로 돌리는 데 필요한 A6 각도까지 관절 한계(여유 5도) 안에 드는 팔꿈치 해가 하나라도 있으면 도달 가능.
        로봇 뒤쪽 쐐기(A1 한계 ±170도 밖 방위)는 팔이 그쪽을 향할 수 없으므로 뺀다. 실제 가능 여부는 IK 추종에서 다시 확인.
        """
        r = self.scene.robot
        L1, L2 = 0.42, 0.40                         # A2-A4, A4-A6 (shared_params 관절 원점)
        wrist = self.P + np.array([0, 0, r.tcp_local[2] + 0.081])
        shoulder = r.base_pos + np.array([0, 0, 0.36])
        rel = wrist - shoulder
        h = np.linalg.norm(rel[..., :2], axis=-1)
        v = rel[..., 2]
        d = np.hypot(h, v)
        c = (d ** 2 - L1 ** 2 - L2 ** 2) / (2 * L1 * L2)
        ok_d = (np.abs(c) <= 1.0) & (d > 0.45)
        phi = np.arctan2(h, v)                       # 연직에서 잰 손목 방향
        lim = np.radians(120.0 - 5.0)
        reach = np.zeros(self.shape, bool)
        for sgn in (1.0, -1.0):
            t4 = sgn * np.arccos(np.clip(c, -1, 1))
            t2 = phi - np.arctan2(L2 * np.sin(t4), L1 + L2 * np.cos(t4))
            t6 = np.pi - t2 - t4                     # 공구가 연직 아래를 향하는 조건
            reach |= (np.abs(t2) <= lim) & (np.abs(t4) <= lim) & (np.abs(t6) <= lim)
        rh = np.linalg.norm(self.P[..., :2] - r.base_pos[:2], axis=-1)
        azim = np.degrees(np.abs(np.arctan2(self.P[..., 1] - r.base_pos[1], self.P[..., 0] - r.base_pos[0])))
        return reach & ok_d & (rh > 0.25) & (azim < np.degrees(r.upper[0]) - 20.0)

    def occupied(self, state: str, carrying: str | None, margin: float):
        key = (state, carrying, round(margin, 4))
        if key in self._occ_cache:
            return self._occ_cache[key]
        layout = self.scene.layout
        objs = _obstacles(layout, state)
        tool = self.scene.params["tool"]
        r = self.scene.robot
        # 공구: TCP에서 플랜지까지 수직 선분 (공구 아래 방향 자세 가정)
        pts = [(np.array([0, 0, z]), tool["radius"]) for z in np.linspace(0, tool["length"], 4)]
        if carrying:
            bed = layout["bed_cartridge"]
            for z in np.linspace(-bed["handle_height"], -(bed["handle_height"] + bed["height"]), 6):
                pts.append((np.array([0, 0, z]), bed["radius"]))
        flat = self.P.reshape(-1, 3)
        occ = np.zeros(len(flat), bool)
        for off, rad in pts:
            Q = flat + off
            for o in objs:
                occ |= dist_point_object(Q, o) < rad + margin
        occ = occ.reshape(self.shape)
        self._occ_cache[key] = occ
        return occ

    def index(self, p):
        return tuple(np.clip(np.round((np.asarray(p) - self.lo) / self.res).astype(int), 0, np.asarray(self.shape) - 1))

    def point(self, idx):
        return self.lo + self.res * np.asarray(idx)


_NEIGH = [d for d in itertools.product((-1, 0, 1), repeat=3) if d != (0, 0, 0)]


def astar(cost_rate: np.ndarray, free: np.ndarray, start, goal, res: float, w_time: float):
    """26-연결 A*. 간선 비용 = 길이 x (평균 선량률 + w_time). 휴리스틱 = 직선거리 x w_time (허용적)."""
    shape = free.shape
    g = {start: 0.0}
    parent = {start: None}
    pq = [(0.0, start)]
    goal_a = np.asarray(goal)
    closed = set()
    while pq:
        _, u = heapq.heappop(pq)
        if u in closed:
            continue
        if u == goal:
            path = []
            while u is not None:
                path.append(u)
                u = parent[u]
            return path[::-1]
        closed.add(u)
        for d in _NEIGH:
            v = (u[0] + d[0], u[1] + d[1], u[2] + d[2])
            if not (0 <= v[0] < shape[0] and 0 <= v[1] < shape[1] and 0 <= v[2] < shape[2]):
                continue
            if not free[v] or v in closed:
                continue
            L = res * np.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
            c = g[u] + L * (0.5 * (cost_rate[u] + cost_rate[v]) + w_time)
            if c < g.get(v, np.inf):
                g[v] = c
                parent[v] = u
                h = res * np.linalg.norm(np.asarray(v) - goal_a) * w_time
                heapq.heappush(pq, (c + h, v))
    return None


def make_b1_planner(fields: dict, notes: list, res: float = 0.04, w_time_quantile: float = 0.5):
    cache = {}

    def planner(scene, step, q_start, q_goal, is_free):
        from .task import apply_state
        r = scene.robot
        if "grid" not in cache:
            cache["grid"] = EEGrid(scene, res)
        G = cache["grid"]
        key = step.field
        if key not in cache:
            flat = G.P.reshape(1, -1, 3)
            n = flat.shape[1]
            # TCP가 공구 아래 방향일 때의 선량률 (운반 중이면 들고 있는 베드도 TCP를 따라 움직임)
            Rdown = np.repeat(tool_down_R(0.0)[None], 1, axis=0)
            rate = fields[key].rate(flat, np.zeros((1, 3)), Rdown, np.zeros(1)) if key != "carry_spent" else None
            if rate is None:
                # 이동 선원: 베드가 TCP에 매달려 있으므로 TCP 자신에 대한 기여는 위치와 무관한 상수.
                # 점 로봇 관점의 비용에는 정적 성분(post)만 의미가 있다.
                rate = fields["post"].rate(flat, np.zeros((1, 3)), Rdown, np.zeros(1))
            cache[key] = rate.reshape(G.shape)
        rate = cache[key]
        free = G.reach & ~G.occupied(step.state, step.carrying, scene.margin)
        p0, R0 = r.tcp_pose(q_start)
        p1, R1 = r.tcp_pose(q_goal)
        s, g = G.index(p0), G.index(p1)
        free = free.copy()
        free[s] = True
        free[g] = True
        w_time = float(np.quantile(rate[free], w_time_quantile))
        vox = astar(rate, free, s, g, G.res, w_time)
        if vox is None:
            notes.append(f"{step.stage} {step.name}: A* 경로 없음 -> 실패")
            return None
        pts = [p0] + [G.point(v) for v in vox[1:-1]] + [p1]
        pts = _smooth(pts, free, G, rate, w_time)
        # 공구는 계속 아래 방향. yaw는 로봇 기준 방위각에 대한 상대값을 시작과 끝 사이에서 선형 보간한다.
        # (절대 yaw를 보간하면 A1이 크게 도는 구간에서 A7이 반대로 한 바퀴 가까이 돌아야 해서 IK가 실패한다)
        def _wrap(a):
            return (a + np.pi) % (2 * np.pi) - np.pi

        base = r.base_pos[:2]
        az = lambda p: np.arctan2(p[1] - base[1], p[0] - base[0])  # noqa: E731
        rel0 = np.arctan2(R0[1, 0], R0[0, 0]) - az(p0)
        drel = _wrap(np.arctan2(R1[1, 0], R1[0, 0]) - az(p1) - rel0)
        L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
        n = max(int(L[-1] / 0.02), 2)
        su = np.linspace(0, L[-1], n + 1)
        P = np.array([np.interp(su, L, np.asarray(pts)[:, i]) for i in range(3)]).T
        qs = [np.asarray(q_start, float)]
        for k in range(1, len(P) - 1):
            frac = su[k] / su[-1]
            Rk = rot_z(az(P[k]) + rel0 + drel * frac) @ tool_down_R(0.0)
            # 영공간 기준 자세: 시작·목표 자세의 관절공간 보간. 끝에서 웨이포인트 자세와 같은 해로 모이게 한다.
            rest = (1 - frac) * np.asarray(q_start, float) + frac * np.asarray(q_goal, float)
            q = r.ik_tcp(P[k], Rk, seed=qs[-1], rest=rest, tol_pos=2e-3, tol_rot=2e-2)
            if q is None or np.max(np.abs(q - qs[-1])) > 0.35:
                notes.append(f"{step.stage} {step.name}: TCP 경로를 팔이 따라가지 못함 (IK, {frac:.0%} 지점)")
                return None
            qs.append(q)
        jump = np.max(np.abs(np.asarray(q_goal, float) - qs[-1]))
        if jump > 0.35:
            # IK 추종 끝 자세와 웨이포인트 자세가 다른 해(팔꿈치·어깨 방향)면 마지막 연결에서 팔이 크게 돈다
            notes.append(f"{step.stage} {step.name}: IK 추종 끝 자세가 목표 자세와 다름 (최대 관절 차 {jump:.2f} rad)")
            return None
        qs.append(np.asarray(q_goal, float))
        for a, b in zip(qs[:-1], qs[1:]):
            if not edge_free(a, b, is_free, 0.03):
                notes.append(f"{step.stage} {step.name}: TCP 경로는 비어 있으나 팔 또는 운반물이 충돌")
                return None
        return qs

    return planner


def _smooth(pts, free, G, rate, w_time):
    """시야선 단축. 직선이 자유 공간이고, 직선의 비용(선량률 + w_time 적분)이 원래 경로보다 크지 않을 때만 줄인다."""
    pts = [np.asarray(p, float) for p in pts]

    def seg_cost(a, b):
        n = max(int(np.linalg.norm(b - a) / (G.res / 2)), 1)
        c = 0.0
        for k in range(n + 1):
            idx = G.index(a + (b - a) * k / n)
            if not free[idx]:
                return np.inf
            c += (rate[idx] + w_time) * (np.linalg.norm(b - a) / n) * (0.5 if k in (0, n) else 1.0)
        return c

    seg = [seg_cost(a, b) for a, b in zip(pts[:-1], pts[1:])]

    def ok(i, j):
        # 직선이 자유 공간을 지나야 하고(유한), 원래 경로보다 비싸지 않아야 한다.
        # 원래 경로 비용이 무한대(끝점 반올림으로 점유 칸을 스친 경우)여도 직선이 유한이면 허용.
        direct = seg_cost(pts[i], pts[j])
        if not np.isfinite(direct):
            return False
        orig = float(np.sum(seg[i:j]))
        return (not np.isfinite(orig)) or direct <= orig * 1.001

    i = 0
    out = [pts[0]]
    while i < len(pts) - 1:
        j = len(pts) - 1
        while j > i + 1 and not ok(i, j):
            j -= 1
        out.append(pts[j])
        i = j
    return out
