"""KUKA LBR iiwa 14 래퍼: 기구학, 역기구학, 경사 중력을 반영한 관절 토크.

- 형상(URDF)은 pybullet_data의 kuka_iiwa/model.urdf, 질량·관성·한계는 shared_params.json 값을 쓴다.
- 공구와 운반 중인 베드는 link_7에 붙은 점질량으로 다룬다 (회전관성 무시).
- pybullet의 calculateInverseDynamics는 첫 호출 때 동역학 트리를 캐시하므로, 링크 질량은 로드 직후에만 바꾼다.
  운반물처럼 바뀌는 질량은 반드시 payloads 인자로 넘긴다.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
import pybullet as p
import pybullet_data

from .geometry import R_to_quat, quat_to_R, rotation_angle, rpy_to_R


@dataclass
class PointMass:
    name: str
    link: int              # pybullet 링크 인덱스 (6 = link_7)
    local_pos: np.ndarray  # 링크 좌표계 위치 [m]
    mass: float            # [kg]


class Robot:
    EE_LINK = 6
    N = 7

    def __init__(self, client: int, params: dict, base_position=(0, 0, 0), base_rpy=(0, 0, 0)):
        self.cid = client
        self.params = params
        urdf = os.path.join(pybullet_data.getDataPath(), "kuka_iiwa", "model.urdf")
        self.base_pos = np.asarray(base_position, float)
        self.base_R = rpy_to_R(base_rpy)
        self.id = p.loadURDF(urdf, self.base_pos.tolist(), R_to_quat(self.base_R), useFixedBase=True,
                             physicsClientId=client)
        rp = params["robot"]
        self.joints = list(range(self.N))
        self.lower = np.asarray(rp["position_lower"], float)
        self.upper = np.asarray(rp["position_upper"], float)
        self.vlim = np.asarray(rp["velocity_limit"], float)
        self.alim = np.asarray(rp["acceleration_limit"], float)
        self.tau_lim = np.asarray(rp["torque_limit"], float)
        self.tau_cap = float(rp.get("torque_utilization_cap", 1.0))

        for j, L in enumerate(rp["links"]):
            info = p.getDynamicsInfo(self.id, j, physicsClientId=client)
            if not np.allclose(info[3], L["com"], atol=1e-6):
                raise ValueError(f"{L['link']} 질량중심이 URDF와 다릅니다: URDF {info[3]} / params {L['com']}")
            p.changeDynamics(self.id, j, mass=L["mass"], localInertiaDiagonal=L["inertia_diag"],
                             physicsClientId=client)
        for j in range(self.N):
            p.changeDynamics(self.id, j, linearDamping=0, angularDamping=0, jointDamping=0,
                             physicsClientId=client)

        self.flange = float(rp["flange_offset_from_link7"])
        tool = params["tool"]
        self.tcp_local = np.array([0.0, 0.0, self.flange + tool["tcp_from_flange"]])
        self.tool_mass = PointMass("tool", self.EE_LINK,
                                   np.array([0.0, 0.0, self.flange + tool["com_from_flange"]]),
                                   float(tool["mass"]))
        self._q = None

    # ------------------------------------------------------------------ 기구학
    def set_q(self, q) -> None:
        q = np.asarray(q, float)
        if self._q is not None and np.array_equal(q, self._q):
            return
        for j in self.joints:
            p.resetJointState(self.id, j, float(q[j]), 0.0, physicsClientId=self.cid)
        self._q = q.copy()

    def invalidate(self) -> None:
        self._q = None

    def link_frames(self, q):
        """링크 좌표계 (7, 3) 위치와 (7, 3, 3) 회전. 인덱스 j = pybullet 링크 j = A(j+1) 관절 위치."""
        self.set_q(q)
        states = p.getLinkStates(self.id, self.joints, computeForwardKinematics=1, physicsClientId=self.cid)
        pos = np.array([s[4] for s in states])
        R = np.array([quat_to_R(s[5]) for s in states])
        return pos, R

    def tcp_pose(self, q):
        pos, R = self.link_frames(q)
        return pos[self.EE_LINK] + R[self.EE_LINK] @ self.tcp_local, R[self.EE_LINK]

    def point_on_link(self, q, link: int, local) -> np.ndarray:
        if link < 0:
            return self.base_pos + self.base_R @ np.asarray(local)
        pos, R = self.link_frames(q)
        return pos[link] + R[link] @ np.asarray(local)

    def in_limits(self, q, margin: float = 0.0) -> bool:
        q = np.asarray(q)
        return bool(np.all(q >= self.lower + margin) and np.all(q <= self.upper - margin))

    def ik_tcp(self, pos, R, seed=None, rest=None, tol_pos=1e-3, tol_rot=1e-2, iters=30):
        """TCP 목표 자세에 대한 역기구학. 실패하면 None.

        rest: 영공간 기준 자세 (같은 TCP 자세에서 팔꿈치 위치를 고를 때 사용)
        """
        pos = np.asarray(pos, float)
        R = np.asarray(R, float)
        target = pos - R @ self.tcp_local          # link_7 좌표계 원점 목표
        quat = R_to_quat(R)
        seed = np.asarray(seed if seed is not None else (rest if rest is not None else np.zeros(self.N)), float)
        rest = np.asarray(rest if rest is not None else seed, float)
        ranges = (self.upper - self.lower).tolist()
        q = np.clip(seed, self.lower, self.upper)
        best, best_err = None, np.inf
        for k in range(iters):
            self.set_q(q)
            if k < iters // 2:
                sol = p.calculateInverseKinematics(
                    self.id, self.EE_LINK, target.tolist(), quat,
                    lowerLimits=self.lower.tolist(), upperLimits=self.upper.tolist(),
                    jointRanges=ranges, restPoses=rest.tolist(),
                    maxNumIterations=200, residualThreshold=1e-7, physicsClientId=self.cid)
            else:
                sol = p.calculateInverseKinematics(
                    self.id, self.EE_LINK, target.tolist(), quat,
                    maxNumIterations=200, residualThreshold=1e-7, physicsClientId=self.cid)
            q = np.clip(np.asarray(sol[: self.N]), self.lower, self.upper)
            self.invalidate()
            tp, tR = self.tcp_pose(q)
            ep, er = np.linalg.norm(tp - pos), rotation_angle(tR, R)
            err = ep / tol_pos + er / tol_rot
            if err < best_err:
                best, best_err = q.copy(), err
            if ep < tol_pos * 0.1 and er < tol_rot * 0.1:
                break
        tp, tR = self.tcp_pose(best)
        ep, er = np.linalg.norm(tp - pos), rotation_angle(tR, R)
        if ep <= tol_pos and er <= tol_rot and self.in_limits(best):
            return best
        return None

    # ------------------------------------------------------------------ 동역학
    def jacobian_point(self, q, link: int, local) -> np.ndarray:
        """링크 좌표계 점 local의 선속도 야코비안 (3, 7). pybullet localPosition은 링크 좌표계 기준."""
        self.set_q(q)
        z = [0.0] * self.N
        lin, _ = p.calculateJacobian(self.id, link, list(map(float, local)), list(map(float, q)), z, z,
                                     physicsClientId=self.cid)
        return np.asarray(lin)

    def inverse_dynamics(self, q, qd, qdd, gravity, payloads=()) -> np.ndarray:
        """관절 토크 (7,). gravity: 선체 좌표계 중력 벡터. 공구 질량은 항상 포함한다.

        점질량 m의 기여: J^T m (J qdd - g). 원심·코리올리 항(J_dot qd)과 회전관성은 무시 (준정적 근사).
        """
        q = list(map(float, q))
        p.setGravity(*map(float, gravity), physicsClientId=self.cid)
        tau = np.asarray(p.calculateInverseDynamics(self.id, q, list(map(float, qd)), list(map(float, qdd)),
                                                    physicsClientId=self.cid))
        g = np.asarray(gravity, float)
        qdd = np.asarray(qdd, float)
        for pm in (self.tool_mass, *payloads):
            if pm.mass <= 0:
                continue
            J = self.jacobian_point(q, pm.link, pm.local_pos)
            tau = tau + J.T @ (pm.mass * (J @ qdd - g))
        return tau

    def static_torque(self, q, gravity, payloads=()) -> np.ndarray:
        z = np.zeros(self.N)
        return self.inverse_dynamics(q, z, z, gravity, payloads)

    def torque_utilization(self, tau) -> np.ndarray:
        return np.abs(tau) / self.tau_lim
