"""PyBullet 핫셀 장면: 배치도에서 장애물 생성, 로봇·공구·운반 베드, 충돌 검사, 스냅샷."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pybullet as p

from . import config
from .geometry import R_to_quat, rot_x, tool_down_R
from .robot import Robot

COLORS = {
    "structure": [0.62, 0.62, 0.60, 1.0],
    "pipe": [0.45, 0.45, 0.43, 1.0],
    "bed_online": [0.92, 0.41, 0.20, 1.0],
    "spent_bed": [0.89, 0.29, 0.28, 1.0],
    "new_bed": [0.11, 0.69, 0.48, 1.0],
    "tool": [0.32, 0.32, 0.31, 1.0],
    "floor": [0.86, 0.86, 0.84, 1.0],
    "wall": [0.93, 0.93, 0.91, 0.25],
}

# 운반 상태: None | "spent" | "new"
CARRY_STATES = (None, "spent", "new")


@dataclass
class EnvLink:
    oid: str
    role: str
    link_index: int


def _shape(kind: str, obj: dict, cid: int, visual: bool, rgba=None):
    """(shape id, 위치, 쿼터니언) 생성. capsule_segment는 선분 방향으로 회전."""
    create = p.createVisualShape if visual else p.createCollisionShape
    extra = {"rgbaColor": rgba} if visual else {}
    if kind == "box":
        sid = create(p.GEOM_BOX, halfExtents=obj["half_extents"], physicsClientId=cid, **extra)
        return sid, list(obj["center"]), [0, 0, 0, 1]
    if kind == "cylinder":
        if visual:
            sid = create(p.GEOM_CYLINDER, radius=obj["radius"], length=obj["height"], physicsClientId=cid, **extra)
        else:
            sid = create(p.GEOM_CYLINDER, radius=obj["radius"], height=obj["height"], physicsClientId=cid)
        return sid, list(obj["center"]), [0, 0, 0, 1]
    if kind == "capsule_segment":
        a, b = np.asarray(obj["start"], float), np.asarray(obj["end"], float)
        d = b - a
        L = float(np.linalg.norm(d))
        z = d / L
        x = np.cross([0, 0, 1.0], z) if abs(z[2]) < 0.99 else np.array([1.0, 0, 0])
        x /= np.linalg.norm(x)
        y = np.cross(z, x)
        R = np.column_stack([x, y, z])
        if visual:
            sid = create(p.GEOM_CAPSULE, radius=obj["radius"], length=L, physicsClientId=cid, **extra)
        else:
            sid = create(p.GEOM_CAPSULE, radius=obj["radius"], height=L, physicsClientId=cid)
        return sid, ((a + b) / 2).tolist(), list(R_to_quat(R))
    raise ValueError(kind)


class Scene:
    def __init__(self, gui: bool = False, layout: dict | None = None, params: dict | None = None,
                 margin: float | None = None):
        self.layout = layout or config.layout()
        self.params = params or config.shared_params()
        self.gui = gui
        self.cid = p.connect(p.GUI if gui else p.DIRECT)
        if gui:
            p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0, physicsClientId=self.cid)
            p.resetDebugVisualizerCamera(2.2, 40, -35, [0.3, 0.0, 0.3], physicsClientId=self.cid)
        rb = self.layout["robot"]
        self.robot = Robot(self.cid, self.params, rb["base_position"], rb["base_rpy"])
        ci = self.params["control_interface"]
        self.margin = margin if margin is not None else ci["d_safe"] + ci["e_track_default"]
        self.bed = self.layout["bed_cartridge"]
        self._build_env()
        self._build_movables()
        self.carrying = None
        self.bed_state = {"spent": "seat_A", "new": "rack"}
        self.reset_state("pre_removal")

    # ------------------------------------------------------------------ 생성
    def _build_env(self):
        objs = self.layout["objects"]
        floor = next(o for o in objs if o["id"] == "floor")
        walls = [o for o in objs if o["id"].startswith("wall")]
        others = [o for o in objs if o["id"] != "floor" and not o["id"].startswith("wall")]
        col, vis, pos, orn = [], [], [], []
        self.env_links: list[EnvLink] = []
        for i, o in enumerate(others):
            role = o.get("role", "structure")
            rgba = COLORS.get(role, COLORS["structure"])
            cs, ps, qs = _shape(o["kind"], o, self.cid, False)
            vs = _shape(o["kind"], o, self.cid, True, rgba)[0]
            fc = np.asarray(floor["center"])
            col.append(cs)
            vis.append(vs)
            pos.append((np.asarray(ps) - fc).tolist())
            orn.append(qs)
            self.env_links.append(EnvLink(o["id"], role, i))
        fcs, fps, _ = _shape("box", floor, self.cid, False)
        fvs, _, _ = _shape("box", floor, self.cid, True, COLORS["floor"])
        n = len(others)
        self.env = p.createMultiBody(
            baseMass=0, baseCollisionShapeIndex=fcs, baseVisualShapeIndex=fvs, basePosition=fps,
            linkMasses=[0] * n, linkCollisionShapeIndices=col, linkVisualShapeIndices=vis,
            linkPositions=pos, linkOrientations=orn, linkInertialFramePositions=[[0, 0, 0]] * n,
            linkInertialFrameOrientations=[[0, 0, 0, 1]] * n, linkParentIndices=[0] * n,
            linkJointTypes=[p.JOINT_FIXED] * n, linkJointAxis=[[0, 0, 1]] * n, physicsClientId=self.cid)
        self.env_link_of = {e.oid: e.link_index for e in self.env_links}
        self.env_link_of["floor"] = -1
        # 벽은 별도 물체: 충돌 검사에는 넣고, 스냅샷을 찍을 때는 치워서 시야를 가리지 않게 한다
        self.walls = []
        for o in walls:
            cs, ps, qs = _shape("box", o, self.cid, False)
            vs = _shape("box", o, self.cid, True, COLORS["wall"])[0]
            self.walls.append((p.createMultiBody(0, cs, vs, ps, qs, physicsClientId=self.cid), ps, qs))

    def _cyl_body(self, radius, height, rgba):
        cs = p.createCollisionShape(p.GEOM_CYLINDER, radius=radius, height=height, physicsClientId=self.cid)
        vs = p.createVisualShape(p.GEOM_CYLINDER, radius=radius, length=height, rgbaColor=rgba,
                                 physicsClientId=self.cid)
        return p.createMultiBody(0, cs, vs, [0, 0, -5], physicsClientId=self.cid)

    def _build_movables(self):
        r, h = self.bed["radius"], self.bed["height"]
        self.bodies = {
            "spent": self._cyl_body(r, h, COLORS["spent_bed"]),
            "new": self._cyl_body(r, h, COLORS["new_bed"]),
        }
        tool = self.params["tool"]
        self.tool_body = self._cyl_body(tool["radius"], tool["length"], COLORS["tool"])
        self.tool_len = tool["length"]

    # ------------------------------------------------------------------ 상태
    def site_center(self, site: str) -> np.ndarray:
        s = self.layout["task_sites"]
        return np.asarray({"seat_A": s["bed_A_center"], "cask": s["cask_place_center"],
                           "rack": s["rack_center"], "hidden": [0, 0, -5]}[site], float)

    def place_bed(self, which: str, site: str):
        self.bed_state[which] = site
        p.resetBasePositionAndOrientation(self.bodies[which], self.site_center(site).tolist(), [0, 0, 0, 1],
                                          physicsClientId=self.cid)

    def reset_state(self, state: str):
        """pre_removal: 사용 후 베드는 Bed A 자리, 신규 베드는 거치대
        post_removal: 사용 후 베드는 캐스크, 신규 베드는 거치대
        installed: 사용 후 베드는 캐스크, 신규 베드는 Bed A 자리"""
        self.carrying = None
        if state == "pre_removal":
            self.place_bed("spent", "seat_A"); self.place_bed("new", "rack")
        elif state == "post_removal":
            self.place_bed("spent", "cask"); self.place_bed("new", "rack")
        elif state == "installed":
            self.place_bed("spent", "cask"); self.place_bed("new", "seat_A")
        else:
            raise ValueError(state)

    def set_carrying(self, which: str | None):
        self.carrying = which

    def bed_pose_from_tcp(self, tcp_pos, tcp_R):
        off = self.bed["handle_height"] + self.bed["height"] / 2
        center = tcp_pos + tcp_R[:, 2] * off
        return center, tcp_R @ rot_x(np.pi)

    def update_attached(self, q):
        pos, R = self.robot.link_frames(q)
        flange = pos[6] + R[6] @ np.array([0, 0, self.robot.flange])
        tool_c = flange + R[6][:, 2] * (self.tool_len / 2)
        p.resetBasePositionAndOrientation(self.tool_body, tool_c.tolist(), R_to_quat(R[6]),
                                          physicsClientId=self.cid)
        if self.carrying:
            tcp = pos[6] + R[6] @ self.robot.tcp_local
            c, Rb = self.bed_pose_from_tcp(tcp, R[6])
            p.resetBasePositionAndOrientation(self.bodies[self.carrying], c.tolist(), R_to_quat(Rb),
                                              physicsClientId=self.cid)

    # ------------------------------------------------------------------ 충돌
    def _hits(self, a, b, margin, link_a=None):
        kw = {"linkIndexA": link_a} if link_a is not None else {}
        return p.getClosestPoints(a, b, margin, physicsClientId=self.cid, **kw)

    def in_collision(self, q, margin: float | None = None, ignore_beds: tuple = (), check_attached: bool = True,
                     return_reason: bool = False):
        """q에서 충돌(또는 여유거리 미달)이면 True.

        ignore_beds: 검사에서 뺄 베드 ("spent", "new"). 파지·내려놓기 직선 구간에서 사용
        check_attached: False면 운반 중인 베드의 충돌은 보지 않음 (거치대 접촉 구간)
        """
        m = self.margin if margin is None else margin
        rid = self.robot.id
        self.update_attached(q)

        def fail(reason):
            return (True, reason) if return_reason else True

        # 1) 로봇 링크 vs 환경 (베이스는 바닥에 고정되어 있으므로 제외)
        for c in self._hits(rid, self.env, m):
            if c[3] >= 0:
                return fail(f"link{c[3]} - env:{self._env_name(c[4])}")
        for wb, _, _ in self.walls:
            if self._hits(rid, wb, m) or self._hits(self.tool_body, wb, m):
                return fail("robot/tool - wall")
        # 2) 공구 vs 환경
        if self._hits(self.tool_body, self.env, m):
            return fail("tool - env")
        # 3) 로봇·공구 vs 베드 (운반 중인 것 제외)
        for which, body in self.bodies.items():
            if which == self.carrying or which in ignore_beds or self.bed_state.get(which) == "hidden":
                continue
            for c in self._hits(rid, body, m):
                if c[3] >= 0:
                    return fail(f"link{c[3]} - bed:{which}")
            if self._hits(self.tool_body, body, m):
                return fail(f"tool - bed:{which}")
        # 4) 운반 중인 베드
        if self.carrying and check_attached:
            cb = self.bodies[self.carrying]
            if self._hits(cb, self.env, m) or any(self._hits(cb, wb, m) for wb, _, _ in self.walls):
                return fail("carried bed - env")
            for which, body in self.bodies.items():
                if which != self.carrying and which not in ignore_beds and self._hits(cb, body, m):
                    return fail("carried bed - bed")
            for c in self._hits(cb, rid, m * 0.5):
                if 0 <= c[4] <= 4:
                    return fail(f"carried bed - link{c[4]}")
        # 5) 자기 충돌 (3칸 이상 떨어진 링크, 공구 vs 아래쪽 링크)
        for i in range(0, 4):
            for j in range(i + 3, 7):
                if p.getClosestPoints(rid, rid, 0.0, linkIndexA=i, linkIndexB=j, physicsClientId=self.cid):
                    return fail(f"self link{i}-link{j}")
        for c in self._hits(self.tool_body, rid, 0.005):
            if c[4] <= 3:
                return fail(f"tool - link{c[4]}")
        return (False, "") if return_reason else False

    def _env_name(self, link_index):
        for e in self.env_links:
            if e.link_index == link_index:
                return e.oid
        return "floor"

    def min_clearance(self, q, max_dist: float = 0.3) -> float:
        """로봇·공구·운반 베드와 환경·베드 사이 최소 거리 (max_dist까지)."""
        self.update_attached(q)
        bodies = [self.robot.id, self.tool_body] + ([self.bodies[self.carrying]] if self.carrying else [])
        targets = [self.env] + [b for w, b in self.bodies.items() if w != self.carrying
                                and self.bed_state.get(w) != "hidden"]
        d = max_dist
        for a in bodies:
            for b in targets:
                for c in p.getClosestPoints(a, b, max_dist, physicsClientId=self.cid):
                    if a == self.robot.id and c[3] <= 0:   # 베이스와 A1 하우징은 바닥 위에 고정된 높이
                        continue
                    d = min(d, c[8])
        return d

    # ------------------------------------------------------------------ 표시
    def snapshot(self, path, q, yaw=40, pitch=-30, dist=2.3, target=(0.3, 0.0, 0.35), size=(900, 640)):
        import matplotlib.pyplot as plt

        self.robot.set_q(q)
        self.update_attached(q)
        for wb, _, _ in self.walls:
            p.resetBasePositionAndOrientation(wb, [0, 0, -50], [0, 0, 0, 1], physicsClientId=self.cid)
        view = p.computeViewMatrixFromYawPitchRoll(target, dist, yaw, pitch, 0, 2, physicsClientId=self.cid)
        proj = p.computeProjectionMatrixFOV(45, size[0] / size[1], 0.05, 10, physicsClientId=self.cid)
        w, h, rgb, _, _ = p.getCameraImage(size[0], size[1], view, proj, renderer=p.ER_TINY_RENDERER,
                                           lightDirection=[1, 1, 2], shadow=0, physicsClientId=self.cid)
        for wb, ps, qs in self.walls:
            p.resetBasePositionAndOrientation(wb, ps, qs, physicsClientId=self.cid)
        img = np.reshape(np.asarray(rgb, dtype=np.uint8), (h, w, 4))[:, :, :3]
        if path is not None:
            plt.imsave(path, img)
        return img

    def disconnect(self):
        p.disconnect(self.cid)


def default_tool_R(target_xy) -> np.ndarray:
    return tool_down_R(float(np.arctan2(target_xy[1], target_xy[0])))
