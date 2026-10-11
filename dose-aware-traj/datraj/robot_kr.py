"""대형 산업용 로봇(KUKA KR QUANTEC) 모델을 PyBullet으로 불러오는 최소 도구.

모델 출처: KUKA 공식 ROS 2 설명 패키지 github.com/kroshu/kuka_robot_descriptions (Apache-2.0).
README가 KR 120/210/300 R2700-2의 관성값과 effort 한계를 검증했다고 표시한다. effort가 최대 토크인지
정격 토크인지는 README에 없다 (refs/notes/12).

xacro 매크로를 ROS 없이 URDF로 바꾼다. 매크로 안에는 ${prefix}, ${package_name}, ${pi}, ${pi/2},
${radians(x)} 만 있어서 문자열 치환으로 충분하다.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np

from . import ROOT

DESC_DIR = ROOT / "data" / "robots" / "kuka_robot_descriptions"
GEN_DIR = ROOT / "data" / "robots" / "generated"
REPO_URL = "https://github.com/kroshu/kuka_robot_descriptions"

MODELS = {
    "kr120": "kr120_r2700_2",
    "kr210": "kr210_r2700_2",
    "kr300": "kr300_r2700_2",
}


def _eval_expr(expr: str) -> str:
    expr = expr.strip()
    if expr == "prefix":
        return ""
    if expr == "package_name":
        return "kuka_quantec_support"
    m = re.fullmatch(r"radians\(([-\d.eE]+)\)", expr)
    if m:
        return repr(math.radians(float(m.group(1))))
    if expr == "pi":
        return repr(math.pi)
    if expr == "pi/2":
        return repr(math.pi / 2)
    raise ValueError(f"처리하지 못한 xacro 식: ${{{expr}}}")


def make_urdf(model: str, desc_dir: Path = DESC_DIR) -> Path:
    name = MODELS[model]
    src = desc_dir / "kuka_quantec_support" / "urdf" / f"{name}_macro.xacro"
    if not src.exists():
        raise FileNotFoundError(
            f"{src} 없음. 먼저 받으세요:\n  git clone --depth 1 {REPO_URL} {desc_dir}")
    text = src.read_text(encoding="utf-8")
    body = re.search(r"<xacro:macro[^>]*>(.*)</xacro:macro>", text, re.S).group(1)
    body = re.sub(r"\$\{([^}]*)\}", lambda m: _eval_expr(m.group(1)), body)
    pkg = (desc_dir / "kuka_quantec_support").as_posix()
    body = body.replace("package://kuka_quantec_support", pkg)
    # 관성 정보가 없는 보조 링크(base, flange, tool0)에 PyBullet이 기본 질량 1 kg을 넣지 않도록 아주 작은 질량을 준다
    tiny = '<inertial><mass value="1e-6"/><inertia ixx="1e-9" ixy="0" ixz="0" iyy="1e-9" iyz="0" izz="1e-9"/></inertial>'
    body = re.sub(r'<link name="([^"]+)"\s*/>', lambda m: f'<link name="{m.group(1)}">{tiny}</link>', body)
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    out = GEN_DIR / f"{name}.urdf"
    out.write_text(f'<?xml version="1.0"?>\n<robot name="{name}">\n{body}\n</robot>\n', encoding="utf-8")
    return out


class KRRobot:
    """6축 KR 로봇. 정적 토크와 IK만 다룬다."""

    def __init__(self, model: str, client):
        import pybullet as p
        self.p, self.cid, self.model = p, client, model
        urdf = make_urdf(model)
        self.uid = p.loadURDF(str(urdf), useFixedBase=True, physicsClientId=client,
                              flags=p.URDF_USE_INERTIA_FROM_FILE)
        self.joints, self.tau_max, self.lower, self.upper = [], [], [], []
        self.flange = None
        for j in range(p.getNumJoints(self.uid, physicsClientId=client)):
            info = p.getJointInfo(self.uid, j, physicsClientId=client)
            if info[2] == p.JOINT_REVOLUTE:
                self.joints.append(j)
                self.tau_max.append(info[10])
                self.lower.append(info[8])
                self.upper.append(info[9])
            if info[12].decode() == "flange":
                self.flange = j
        self.tau_max = np.array(self.tau_max)
        self.mass = sum(p.getDynamicsInfo(self.uid, j, physicsClientId=client)[0]
                        for j in range(-1, p.getNumJoints(self.uid, physicsClientId=client)))

    def set_q(self, q):
        for j, v in zip(self.joints, q):
            self.p.resetJointState(self.uid, j, float(v), physicsClientId=self.cid)

    def flange_pose(self, q):
        self.set_q(q)
        s = self.p.getLinkState(self.uid, self.flange, computeForwardKinematics=True, physicsClientId=self.cid)
        return np.array(s[4]), np.array(self.p.getMatrixFromQuaternion(s[5])).reshape(3, 3)

    def ik(self, pos, quat, iters=200):
        q = self.p.calculateInverseKinematics(self.uid, self.flange, pos, quat,
                                              lowerLimits=self.lower, upperLimits=self.upper,
                                              jointRanges=list(np.array(self.upper) - np.array(self.lower)),
                                              restPoses=[0, -1.57, 1.57, 0, 1.2, 0],
                                              maxNumIterations=iters, residualThreshold=1e-5,
                                              physicsClientId=self.cid)
        q = np.array(q[:len(self.joints)])
        p_fk, _ = self.flange_pose(q)
        return q, float(np.linalg.norm(p_fk - np.asarray(pos)))

    def static_torque(self, q, g, mass=0.0, com_world_offset=None):
        """중력 g(로봇 베이스 좌표)에서 정적 관절 토크. 질량 mass를 플랜지 기준 점(월드 오프셋)에 매단다."""
        self.p.setGravity(*g, physicsClientId=self.cid)
        tau = np.array(self.p.calculateInverseDynamics(self.uid, list(map(float, q)), [0.0] * len(q),
                                                       [0.0] * len(q), physicsClientId=self.cid))
        if mass > 0:
            pos, _ = self.flange_pose(q)
            point = pos + (np.zeros(3) if com_world_offset is None else np.asarray(com_world_offset))
            J_lin, _ = self.p.calculateJacobian(self.uid, self.flange, list((point - pos) @ self._flange_R(q)),
                                                list(map(float, q)), [0.0] * len(q), [0.0] * len(q),
                                                physicsClientId=self.cid)
            F = mass * np.asarray(g)
            tau = tau - np.asarray(J_lin).T @ F
        return tau

    def _flange_R(self, q):
        _, R = self.flange_pose(q)
        return R
