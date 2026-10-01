"""시간 매개변수화: TOPP-RA (관절 속도·가속도 한계 안 최단시간) + 속도 비율 alpha, 없으면 대체 방식."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    import toppra as ta
    import toppra.algorithm as ta_algo
    import toppra.constraint as ta_con

    ta.setup_logging("WARNING")
    HAVE_TOPPRA = True
except Exception:  # noqa: BLE001
    HAVE_TOPPRA = False


@dataclass
class Trajectory:
    t: np.ndarray      # (T,)
    q: np.ndarray      # (T, 7)
    qd: np.ndarray
    qdd: np.ndarray
    method: str = ""

    @property
    def duration(self) -> float:
        return float(self.t[-1] - self.t[0]) if len(self.t) else 0.0

    def shifted(self, t0: float) -> "Trajectory":
        return Trajectory(self.t + t0, self.q, self.qd, self.qdd, self.method)


def _param(path: np.ndarray) -> np.ndarray:
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    keep = np.concatenate([[True], np.diff(s) > 1e-9])
    return s, keep


def topp(path: np.ndarray, vlim, alim, dt: float = 0.01, alpha: float = 1.0, gridpoints: int = 0,
         torque=None) -> Trajectory:
    """경로(관절 점열)를 지나는 최단시간 궤적. alpha < 1 이면 속도 비율을 줄인다 (시간 x 1/alpha).

    torque: (inv_dyn 함수 목록, 토크 한계 (7,)) 를 주면 각 inv_dyn(q, qd, qdd)에 대해 |tau| <= 한계를 제약으로 넣는다.
            경사 조건마다 inv_dyn을 하나씩 넣으면 포락선 전체에서 토크 한계를 지킨다.
    TOPP-RA가 설치되어 있지 않으면 quintic 시간 척도로 대신한다 (토크 제약은 사후 점검만).
    """
    path = np.asarray(path, float)
    s, keep = _param(path)
    path, s = path[keep], s[keep]
    if len(path) < 2 or s[-1] < 1e-9:
        return Trajectory(np.array([0.0]), path[:1], np.zeros((1, path.shape[1])), np.zeros((1, path.shape[1])), "static")
    vlim = np.asarray(vlim, float) * alpha
    alim = np.asarray(alim, float) * alpha ** 2
    if HAVE_TOPPRA:
        try:
            return _topp_toppra(path, s / s[-1], vlim, alim, dt, gridpoints, torque)
        except Exception as e:  # noqa: BLE001
            print(f"[timing] TOPP-RA 실패, 대체 방식 사용: {e}")
    return _topp_quintic(path, s / s[-1], vlim, alim, dt)


def _topp_toppra(path, ss, vlim, alim, dt, gridpoints, torque=None):
    spline = ta.SplineInterpolator(ss, path, bc_type="clamped")
    pc_v = ta_con.JointVelocityConstraint(np.column_stack([-vlim, vlim]))
    pc_a = ta_con.JointAccelerationConstraint(np.column_stack([-alim, alim]))
    cons = [pc_v, pc_a]
    if torque:
        funcs, tau_max = torque
        tau_max = np.asarray(tau_max, float)
        for f in funcs:
            cons.append(ta_con.JointTorqueConstraint(
                f, np.column_stack([-tau_max, tau_max]), np.zeros(len(tau_max)),
                discretization_scheme=ta_con.DiscretizationType.Interpolation))
    n_grid = gridpoints or int(np.clip(len(path) * (6 if torque else 3), 100, 1000))
    grid = np.linspace(0, ss[-1], n_grid)
    inst = ta_algo.TOPPRA(cons, spline, gridpoints=grid, parametrizer="ParametrizeConstAccel")
    jt = inst.compute_trajectory(0, 0)
    if jt is None:
        raise RuntimeError("compute_trajectory returned None")
    T = jt.duration
    t = np.arange(0.0, T, dt)
    t = np.append(t, T) if T - t[-1] > 1e-9 else t
    return Trajectory(t, jt(t), jt(t, 1), jt(t, 2), "toppra")


def _topp_quintic(path, ss, vlim, alim, dt):
    from scipy.interpolate import CubicSpline

    cs = CubicSpline(ss, path, bc_type="clamped")
    sg = np.linspace(0, 1, 400)
    dq, ddq = np.abs(cs(sg, 1)), np.abs(cs(sg, 2))

    def ok(T):
        tau = np.linspace(0, 1, 400)
        s = 10 * tau ** 3 - 15 * tau ** 4 + 6 * tau ** 5
        sd = (30 * tau ** 2 - 60 * tau ** 3 + 30 * tau ** 4) / T
        sdd = (60 * tau - 180 * tau ** 2 + 120 * tau ** 3) / T ** 2
        v = np.abs(cs(s, 1)) * sd[:, None]
        a = np.abs(cs(s, 2) * sd[:, None] ** 2 + cs(s, 1) * sdd[:, None])
        return np.all(v <= vlim * 1.0001) and np.all(a <= alim * 1.0001)

    lo, hi = 1e-3, 1.0
    while not ok(hi):
        hi *= 2
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if ok(mid) else (mid, hi)
    T = hi
    t = np.arange(0.0, T, dt)
    t = np.append(t, T)
    tau = t / T
    s = 10 * tau ** 3 - 15 * tau ** 4 + 6 * tau ** 5
    sd = (30 * tau ** 2 - 60 * tau ** 3 + 30 * tau ** 4) / T
    sdd = (60 * tau - 180 * tau ** 2 + 120 * tau ** 3) / T ** 2
    q = cs(s)
    qd = cs(s, 1) * sd[:, None]
    qdd = cs(s, 2) * sd[:, None] ** 2 + cs(s, 1) * sdd[:, None]
    return Trajectory(t, q, qd, qdd, "quintic")


def fine_motion(path: np.ndarray, tcp_length: float, v_tcp: float, vlim, alim, dt: float = 0.01) -> Trajectory:
    """접촉 근처 직선 구간: TCP 평균 속도 v_tcp 이하가 되도록 quintic 시간 척도 (관절 한계도 만족)."""
    path = np.asarray(path, float)
    s, keep = _param(path)
    path, s = path[keep], s[keep]
    if len(path) < 2:
        return dwell(path[0], 0.0)
    traj = _topp_quintic(path, s / s[-1], np.asarray(vlim), np.asarray(alim), dt)
    T_cart = 1.875 * tcp_length / v_tcp          # quintic 최고속도 = 평균의 1.875배
    if traj.duration >= T_cart:
        return traj
    scale = T_cart / traj.duration
    t = np.arange(0.0, T_cart, dt)
    t = np.append(t, T_cart)
    from scipy.interpolate import interp1d

    f = interp1d(traj.t * scale, traj.q, axis=0)
    fd = interp1d(traj.t * scale, traj.qd / scale, axis=0)
    fdd = interp1d(traj.t * scale, traj.qdd / scale ** 2, axis=0)
    t = np.clip(t, 0, traj.t[-1] * scale)
    return Trajectory(t, f(t), fd(t), fdd(t), "fine")


def dwell(q, duration: float, step: float = 1.0) -> Trajectory:
    """정지 구간. 선량 적분은 양 끝 두 점이면 정확하지만, 그림과 CSV를 위해 step 간격으로 샘플링한다."""
    q = np.asarray(q, float)
    n = max(int(np.ceil(duration / step)), 1) + 1
    t = np.linspace(0.0, duration, n)
    Q = np.repeat(q[None, :], n, axis=0)
    return Trajectory(t, Q, np.zeros_like(Q), np.zeros_like(Q), "dwell")
