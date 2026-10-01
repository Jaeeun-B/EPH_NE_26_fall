"""관절공간 경로계획: RRT-Connect, 경로 단축, 직선(데카르트) 구간 IK 추종."""
from __future__ import annotations

import time
from typing import Callable

import numpy as np


def edge_free(qa, qb, is_free: Callable, res: float = 0.03) -> bool:
    d = np.max(np.abs(qb - qa))
    n = max(int(np.ceil(d / res)), 1)
    for k in range(1, n + 1):
        if not is_free(qa + (qb - qa) * (k / n)):
            return False
    return True


class _Tree:
    def __init__(self, root):
        self.nodes = [np.asarray(root, float)]
        self.parent = [-1]
        self._arr = np.asarray([root], float)

    def add(self, q, parent):
        self.nodes.append(q)
        self.parent.append(parent)
        self._arr = np.vstack([self._arr, q])
        return len(self.nodes) - 1

    def nearest(self, q):
        return int(np.argmin(np.sum((self._arr - q) ** 2, axis=1)))

    def path_to_root(self, i):
        out = []
        while i >= 0:
            out.append(self.nodes[i])
            i = self.parent[i]
        return out


def rrt_connect(q_start, q_goal, is_free: Callable, lower, upper, step: float = 0.2, res: float = 0.03,
                max_iter: int = 20000, time_limit: float = 60.0, rng=None, goal_bias: float = 0.05):
    """양방향 RRT-Connect. 경로(관절 배열 리스트) 또는 None.

    is_free(q) -> bool : 충돌이 없고 여유거리를 만족하면 True
    """
    rng = rng or np.random.default_rng()
    q_start, q_goal = np.asarray(q_start, float), np.asarray(q_goal, float)
    if not is_free(q_start):
        raise ValueError("시작 자세가 충돌 상태입니다")
    if not is_free(q_goal):
        raise ValueError("목표 자세가 충돌 상태입니다")
    if edge_free(q_start, q_goal, is_free, res):
        return [q_start, q_goal]
    lower, upper = np.asarray(lower), np.asarray(upper)
    ta, tb = _Tree(q_start), _Tree(q_goal)
    a_is_start = True
    t0 = time.time()

    def extend(tree, q):
        i = tree.nearest(q)
        qn = tree.nodes[i]
        d = q - qn
        dist = np.linalg.norm(d)
        q_new = q if dist <= step else qn + d * (step / dist)
        if edge_free(qn, q_new, is_free, res):
            j = tree.add(q_new, i)
            return ("reached" if dist <= step else "advanced"), j
        return "trapped", None

    def connect(tree, q):
        while True:
            status, j = extend(tree, q)
            if status != "advanced":
                return status, j

    for it in range(max_iter):
        if time.time() - t0 > time_limit:
            break
        target = (q_goal if a_is_start else q_start) if rng.random() < goal_bias else rng.uniform(lower, upper)
        status, j = extend(ta, target)
        if status != "trapped":
            status_b, k = connect(tb, ta.nodes[j])
            if status_b == "reached":
                pa = ta.path_to_root(j)[::-1]
                pb = tb.path_to_root(k)
                path = pa + pb[1:]
                return path if a_is_start else path[::-1]
        ta, tb = tb, ta
        a_is_start = not a_is_start
    return None


def shortcut(path, is_free: Callable, iters: int = 300, res: float = 0.03, rng=None):
    rng = rng or np.random.default_rng()
    path = [np.asarray(q, float) for q in path]
    for _ in range(iters):
        if len(path) <= 2:
            break
        i, j = sorted(rng.choice(len(path), 2, replace=False))
        if j - i < 2:
            continue
        if edge_free(path[i], path[j], is_free, res):
            path = path[: i + 1] + path[j:]
    return path


def densify(path, max_step: float = 0.05) -> np.ndarray:
    out = [np.asarray(path[0], float)]
    for qa, qb in zip(path[:-1], path[1:]):
        n = max(int(np.ceil(np.max(np.abs(qb - qa)) / max_step)), 1)
        for k in range(1, n + 1):
            out.append(qa + (qb - qa) * (k / n))
    return np.asarray(out)


def path_length(path) -> float:
    path = np.asarray(path)
    return float(np.sum(np.linalg.norm(np.diff(path, axis=0), axis=1)))


def cartesian_line(robot, q_start, p_goal, R_goal, n_steps: int | None = None, step: float = 0.005,
                   max_joint_jump: float = 0.15):
    """TCP를 현재 자세에서 p_goal까지 직선으로 옮기는 관절 경로. 자세는 R_goal로 고정.

    연속성을 위해 매 점에서 직전 해를 초기값·영공간 기준으로 IK를 푼다. 실패하면 None.
    """
    p0, R0 = robot.tcp_pose(q_start)
    p_goal = np.asarray(p_goal, float)
    L = np.linalg.norm(p_goal - p0)
    n = n_steps or max(int(np.ceil(L / step)), 2)
    qs = [np.asarray(q_start, float)]
    for k in range(1, n + 1):
        pk = p0 + (p_goal - p0) * (k / n)
        q = robot.ik_tcp(pk, R_goal, seed=qs[-1], rest=qs[-1], tol_pos=5e-4, tol_rot=5e-3)
        if q is None or np.max(np.abs(q - qs[-1])) > max_joint_jump:
            return None
        qs.append(q)
    return np.asarray(qs)


def make_rrt_planner(task: dict, rng=None):
    """B0: RRT-Connect + 경로 단축. 선량을 보지 않는 시간 최소 기준선의 경로 부분."""
    pl = task["planner"]
    rng = rng or np.random.default_rng(pl["seed"])

    def planner(scene, step, q_start, q_goal, is_free):
        r = scene.robot
        lo, hi = r.lower + 0.02, r.upper - 0.02
        path = rrt_connect(q_start, q_goal, is_free, lo, hi, step=pl["rrt_step"], res=pl["edge_resolution"],
                           max_iter=pl["max_iter"], time_limit=pl["time_limit"], rng=rng)
        if path is None:
            return None
        return shortcut(path, is_free, iters=pl["shortcut_iters"], res=pl["edge_resolution"], rng=rng)

    return planner
