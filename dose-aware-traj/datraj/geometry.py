"""회전 행렬, 경사 중력, 기본 도형 거리 계산."""
from __future__ import annotations

import numpy as np

G0 = 9.81


def rot_x(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def rpy_to_R(rpy) -> np.ndarray:
    r, p, y = rpy
    return rot_z(y) @ rot_y(p) @ rot_x(r)


def quat_to_R(q) -> np.ndarray:
    """pybullet 쿼터니언 (x, y, z, w) -> 회전 행렬."""
    x, y, z, w = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def R_to_quat(R: np.ndarray) -> tuple:
    """회전 행렬 -> pybullet 쿼터니언 (x, y, z, w)."""
    R = np.asarray(R, dtype=float)
    tr = np.trace(R)
    if tr > 0:
        s = np.sqrt(tr + 1.0) * 2
        w = 0.25 * s
        x = (R[2, 1] - R[1, 2]) / s
        y = (R[0, 2] - R[2, 0]) / s
        z = (R[1, 0] - R[0, 1]) / s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2
        w = (R[2, 1] - R[1, 2]) / s
        x = 0.25 * s
        y = (R[0, 1] + R[1, 0]) / s
        z = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2
        w = (R[0, 2] - R[2, 0]) / s
        x = (R[0, 1] + R[1, 0]) / s
        y = 0.25 * s
        z = (R[1, 2] + R[2, 1]) / s
    else:
        s = np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2
        w = (R[1, 0] - R[0, 1]) / s
        x = (R[0, 2] + R[2, 0]) / s
        y = (R[1, 2] + R[2, 1]) / s
        z = 0.25 * s
    q = np.array([x, y, z, w])
    return tuple(q / np.linalg.norm(q))


def rotation_angle(Ra: np.ndarray, Rb: np.ndarray) -> float:
    """두 회전 사이의 각도 차이 (rad)."""
    c = (np.trace(Ra.T @ Rb) - 1.0) / 2.0
    return float(np.arccos(np.clip(c, -1.0, 1.0)))


def tool_down_R(yaw: float = 0.0) -> np.ndarray:
    """공구 z축이 연직 아래를 향하는 자세. yaw는 연직축 회전."""
    return rot_z(yaw) @ rot_x(np.pi)


def tool_pointing_R(direction, up_hint=(0.0, 0.0, 1.0)) -> np.ndarray:
    """공구 z축이 direction을 향하는 자세."""
    z = np.asarray(direction, float)
    z = z / np.linalg.norm(z)
    up = np.asarray(up_hint, float)
    if abs(np.dot(up, z)) > 0.95:
        up = np.array([1.0, 0.0, 0.0])
    x = np.cross(up, z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    return np.column_stack([x, y, z])


def ship_gravity(roll_deg: float, pitch_deg: float, g: float = G0) -> np.ndarray:
    """선체 고정 좌표계에서 본 중력 벡터.

    g_ship = R_y(pitch)^T R_x(roll)^T [0, 0, -g]
    경사 0도면 [0, 0, -g]. 부호 규약은 shared_params.json의 inclination_envelope와 같다.
    """
    r, p = np.deg2rad(roll_deg), np.deg2rad(pitch_deg)
    return rot_y(p).T @ rot_x(r).T @ np.array([0.0, 0.0, -g])


# ---------------------------------------------------------------------------
# 기본 도형까지의 거리 (B1의 점유 격자, 배치 점검용)
# ---------------------------------------------------------------------------

def dist_point_box(P: np.ndarray, center, half) -> np.ndarray:
    """축 정렬 박스까지의 부호 거리. P: (N, 3)."""
    d = np.abs(P - np.asarray(center)) - np.asarray(half)
    outside = np.linalg.norm(np.maximum(d, 0.0), axis=-1)
    inside = np.minimum(np.max(d, axis=-1), 0.0)
    return outside + inside


def dist_point_vcylinder(P: np.ndarray, center, radius, height) -> np.ndarray:
    """z축 방향 원기둥까지의 부호 거리."""
    c = np.asarray(center)
    q = P - c
    dr = np.linalg.norm(q[..., :2], axis=-1) - radius
    dz = np.abs(q[..., 2]) - height / 2.0
    d = np.stack([dr, dz], axis=-1)
    outside = np.linalg.norm(np.maximum(d, 0.0), axis=-1)
    inside = np.minimum(np.max(d, axis=-1), 0.0)
    return outside + inside


def dist_point_segment(P: np.ndarray, a, b) -> np.ndarray:
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    ab = b - a
    t = np.clip(((P - a) @ ab) / max(ab @ ab, 1e-12), 0.0, 1.0)
    proj = a + t[..., None] * ab
    return np.linalg.norm(P - proj, axis=-1)


def dist_point_object(P: np.ndarray, obj: dict) -> np.ndarray:
    kind = obj["kind"]
    if kind == "box":
        return dist_point_box(P, obj["center"], obj["half_extents"])
    if kind == "cylinder":
        return dist_point_vcylinder(P, obj["center"], obj["radius"], obj["height"])
    if kind == "capsule_segment":
        return dist_point_segment(P, obj["start"], obj["end"]) - obj["radius"]
    raise ValueError(f"unknown kind {kind}")
