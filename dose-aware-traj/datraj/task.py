"""베드 교체 작업 S1~S6: 웨이포인트, 장면 상태, 단계별 구간, 궤적 조립."""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from . import config
from .geometry import ship_gravity, tool_down_R
from .robot import PointMass
from .planning import cartesian_line, densify, edge_free
from .timing import Trajectory, dwell, fine_motion, topp

STAGES = ["S1", "S2", "S3", "S4", "S5", "S6"]
STAGE_NAMES = {"S1": "접근", "S2": "해제", "S3": "반출", "S4": "장착 이동", "S5": "체결", "S6": "복귀"}


@dataclass
class Step:
    stage: str
    kind: str                     # plan | line | dwell
    name: str
    goal: str | None              # 웨이포인트 이름 (dwell은 None)
    state: str                    # pre_removal | carry_spent | post_removal | carry_new | installed
    field: str                    # pre | post | carry_spent
    ignore_beds: tuple = ()
    check_attached: bool = True
    dwell_key: str | None = None

    @property
    def carrying(self):
        return {"carry_spent": "spent", "carry_new": "new"}.get(self.state)


def task_steps() -> list[Step]:
    S = Step
    return [
        S("S1", "plan", "대기→Bed A 위", "approach_A", "pre_removal", "pre"),
        S("S1", "line", "손잡이로 하강", "grasp_A", "pre_removal", "pre", ("spent",)),
        S("S2", "dwell", "커플링 해제·파지", None, "pre_removal", "pre", ("spent",), dwell_key="S2_dwell"),
        S("S3", "line", "노즐 분리 (-x)", "disengaged_A", "carry_spent", "carry_spent", check_attached=False),
        S("S3", "line", "들어올림", "lifted_A", "carry_spent", "carry_spent", check_attached=False),
        S("S3", "plan", "캐스크로 운반", "cask_above", "carry_spent", "carry_spent"),
        S("S3", "line", "캐스크에 내려놓기", "cask_place", "carry_spent", "carry_spent", check_attached=False),
        S("S3", "dwell", "놓기", None, "carry_spent", "carry_spent", check_attached=False, dwell_key="release_dwell"),
        S("S4", "line", "캐스크에서 후퇴", "cask_retreat", "post_removal", "post", ("spent",)),
        S("S4", "plan", "신규 베드 위로", "rack_above", "post_removal", "post"),
        S("S4", "line", "신규 베드로 하강", "rack_grasp", "post_removal", "post", ("new",)),
        S("S4", "dwell", "파지", None, "post_removal", "post", ("new",), dwell_key="grasp_dwell"),
        S("S4", "line", "신규 베드 들어올림", "rack_lift", "carry_new", "post", check_attached=False),
        S("S4", "plan", "Bed A 자리로 운반", "install_above", "carry_new", "post"),
        S("S4", "line", "내려놓기", "install_lowered", "carry_new", "post", check_attached=False),
        S("S4", "line", "노즐 결합 (+x)", "grasp_A", "carry_new", "post", check_attached=False),
        S("S5", "dwell", "커플링 체결", None, "installed", "post", ("new",), dwell_key="S5_dwell"),
        S("S6", "line", "상승", "approach_A", "installed", "post", ("new",)),
        S("S6", "plan", "대기 위치로 복귀", "home", "installed", "post"),
    ]


def payloads_for(step: Step, robot, params) -> list[PointMass]:
    """운반 중인 베드를 link_7의 점질량으로."""
    if step.carrying is None:
        return []
    off = params["payload"]["bed_com_from_tcp"]
    m = params["payload"]["bed_spent_mass" if step.carrying == "spent" else "bed_new_mass"]
    return [PointMass(f"bed_{step.carrying}", robot.EE_LINK, robot.tcp_local + np.array([0.0, 0.0, off]), m)]


def torque_constraint(scene, step: Step, extra_payloads=()):
    """경사 포락선의 각 조건에 대한 역동역학 함수 목록과 토크 상한 (cap x 한계)."""
    r, params = scene.robot, scene.params
    pl = payloads_for(step, r, params) + list(extra_payloads)
    funcs = []
    for c in params["inclination_envelope"]["cases"]:
        g = ship_gravity(c["roll_deg"], c["pitch_deg"])
        funcs.append(lambda q, qd, qdd, g=g: r.inverse_dynamics(q, qd, qdd, g, pl))
    # 격자점 사이 이산화 오차를 흡수하도록 3% 여유를 더 둔다
    return funcs, r.tau_lim * r.tau_cap * 0.97


def waypoints(layout: dict | None = None, task: dict | None = None) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    layout = layout or config.layout()
    task = task or config.task_config()
    bed, sites, g = layout["bed_cartridge"], layout["task_sites"], task["geometry"]
    up = np.array([0.0, 0.0, 1.0])
    grip = bed["height"] / 2 + bed["handle_height"]

    def yaw(p):
        return float(np.arctan2(p[1], p[0]) + np.pi)

    A = np.asarray(sites["bed_A_center"], float)
    cask = np.asarray(sites["cask_place_center"], float)
    rack = np.asarray(sites["rack_center"], float)
    dis = np.asarray(sites["coupling_disengage_dir"], float) * sites["coupling_disengage_dist"]
    wp = {}
    RA, RC, RR = tool_down_R(yaw(A)), tool_down_R(yaw(cask)), tool_down_R(yaw(rack))
    wp["grasp_A"] = (A + up * grip, RA)
    wp["approach_A"] = (wp["grasp_A"][0] + up * g["approach_height"], RA)
    wp["disengaged_A"] = (wp["grasp_A"][0] + dis + up * g["disengage_lift"], RA)
    wp["lifted_A"] = (wp["disengaged_A"][0] + up * g["lift_height"], RA)
    wp["install_above"] = wp["lifted_A"]
    wp["install_lowered"] = wp["disengaged_A"]
    wp["cask_place"] = (cask + up * (grip + g["place_clearance"]), RC)
    wp["cask_above"] = (wp["cask_place"][0] + up * g["approach_height"], RC)
    wp["cask_retreat"] = wp["cask_above"]
    wp["rack_grasp"] = (rack + up * grip, RR)
    wp["rack_above"] = (wp["rack_grasp"][0] + up * g["approach_height"], RR)
    wp["rack_lift"] = (wp["rack_grasp"][0] + up * g["lift_height"], RR)
    return wp


def apply_state(scene, state: str) -> None:
    if state in ("pre_removal", "post_removal", "installed"):
        scene.reset_state(state)
    elif state == "carry_spent":
        scene.place_bed("new", "rack")
        scene.bed_state["spent"] = "carried"
        scene.set_carrying("spent")
    elif state == "carry_new":
        scene.place_bed("spent", "cask")
        scene.bed_state["new"] = "carried"
        scene.set_carrying("new")
    else:
        raise ValueError(state)


def make_is_free(scene, step: Step, margin=None, static_torque: bool = True, torque_margin: float = 0.95,
                 extra_payloads=(), limit_tol: float = 0.0):
    """관절 한계, 충돌·여유거리, (운반 중이면) 경사 포락선 정적 토크를 모두 만족하면 True.

    운반 중에 공구를 기울이면 매달린 베드 때문에 A6(40 N·m)가 먼저 한계에 닿는다.
    정적 토크가 cap x torque_margin 을 넘는 자세는 아예 탐색에서 뺀다 (남은 여유는 가감속용).
    """
    r = scene.robot
    check_tau = static_torque and (step.carrying is not None or len(extra_payloads) > 0)
    if check_tau:
        funcs, tau_max = torque_constraint(scene, step, extra_payloads)
        z = np.zeros(r.N)

    def is_free(q):
        if not r.in_limits(q, margin=-limit_tol):
            return False
        if check_tau:
            for f in funcs:
                if np.any(np.abs(f(q, z, z)) > tau_max * torque_margin):
                    return False
        return not scene.in_collision(q, margin=margin, ignore_beds=step.ignore_beds,
                                      check_attached=step.check_attached)
    return is_free


# ---------------------------------------------------------------------------
# 웨이포인트 관절각 풀기 (모든 계획기가 같은 관절 웨이포인트를 쓴다)
# ---------------------------------------------------------------------------

@dataclass
class SolvedStep:
    step: Step
    q_start: np.ndarray
    q_goal: np.ndarray
    line_path: np.ndarray | None = None


def _ik_candidates(scene, pos, R, seeds):
    sols = []
    for yaw_off in (0.0, np.pi / 2, -np.pi / 2):
        from .geometry import rot_z
        Rk = rot_z(yaw_off) @ R
        for s in seeds:
            q = scene.robot.ik_tcp(pos, Rk, seed=s, rest=s)
            if q is not None and not any(np.allclose(q, o, atol=1e-3) for o, _ in sols):
                sols.append((q, Rk))
    return sols


def _score(scene, q, q_prev, step):
    r = scene.robot
    margin = np.min(np.minimum(q - r.lower, r.upper - q) / (r.upper - r.lower))
    clear = scene.min_clearance(q)
    return 2.0 * margin + 1.0 * min(clear, 0.15) - 0.05 * np.linalg.norm(q - q_prev)


def solve_chain(scene, task: dict | None = None, layout: dict | None = None, verbose: bool = True) -> list[SolvedStep]:
    task = task or config.task_config()
    layout = layout or config.layout()
    wp = waypoints(layout, task)
    steps = task_steps()
    rests = [np.asarray(r, float) for r in task["ik_rest_candidates"]]
    q_home = np.asarray(task["home_q"], float)

    def solve_from(i, q_cur, R_cur):
        """i번째 단계부터 끝까지 푼다 (계획 목표는 후보를 바꿔가며 뒤 직선 구간이 풀리는 것을 고른다)."""
        out = []
        while i < len(steps):
            st = steps[i]
            apply_state(scene, st.state)
            if st.kind == "dwell":
                out.append(SolvedStep(st, q_cur, q_cur))
                i += 1
                continue
            if st.kind == "line":
                pos, R = wp[st.goal]
                R = R_cur if R_cur is not None else R
                path = cartesian_line(scene.robot, q_cur, pos, R)
                if path is None:
                    return None, f"{st.name}: 직선 IK 실패"
                free = make_is_free(scene, st)
                bad = [k for k in range(0, len(path), 3) if not free(path[k])]
                if bad:
                    _, why = scene.in_collision(path[bad[0]], ignore_beds=st.ignore_beds,
                                                check_attached=st.check_attached, return_reason=True)
                    return None, f"{st.name}: 직선 구간 충돌 ({why})"
                out.append(SolvedStep(st, q_cur, path[-1], path))
                q_cur = path[-1]
                i += 1
                continue
            # plan
            if st.goal == "home":
                cands = [(q_home, None)]
            else:
                pos, R = wp[st.goal]
                cands = _ik_candidates(scene, pos, R, [q_cur] + rests)
            free = make_is_free(scene, st)
            cands = [(q, Rk) for q, Rk in cands if free(q)]
            cands.sort(key=lambda c: -_score(scene, c[0], q_cur, st))
            cands = cands[:6]
            last_err = f"{st.name}: 충돌 없는 IK 해 없음"
            for q_goal, Rk in cands:
                rest, err = solve_from(i + 1, q_goal, Rk)
                if rest is not None:
                    return out + [SolvedStep(st, q_cur, q_goal)] + rest, ""
                last_err = err
            return None, last_err
        return out, ""

    t0 = time.time()
    solved, err = solve_from(0, q_home, None)
    if solved is None:
        raise RuntimeError(f"웨이포인트를 풀지 못했습니다: {err}")
    if verbose:
        print(f"웨이포인트 IK 완료 ({time.time() - t0:.1f} s, 단계 {len(solved)}개)")
    return solved


# ---------------------------------------------------------------------------
# 궤적 조립
# ---------------------------------------------------------------------------

@dataclass
class Segment:
    step: Step
    traj: Trajectory
    joint_path: np.ndarray
    plan_time: float = 0.0
    info: dict = field(default_factory=dict)


def _traj_collision_free(scene, step, traj: Trajectory, every: int = 4) -> bool:
    # 시간 매개변수화 뒤 점검: 스플라인이 관절 한계를 0.005 rad 이내로 넘는 것은 허용
    free = make_is_free(scene, step, margin=scene.margin * 0.5, limit_tol=0.005)
    return all(free(traj.q[k]) for k in range(0, len(traj.q), every))


def _stop_and_go(path, vlim, alim, dt):
    """경로 꼭짓점마다 멈추는 궤적 (스플라인 과주행이 충돌을 만들 때의 대체안)."""
    from .timing import _topp_quintic
    parts, t0 = [], 0.0
    for qa, qb in zip(path[:-1], path[1:]):
        tr = _topp_quintic(np.vstack([qa, (qa + qb) / 2, qb]), np.array([0, 0.5, 1.0]), vlim, alim, dt)
        parts.append(tr.shifted(t0) if not parts else Trajectory(tr.t[1:] + t0, tr.q[1:], tr.qd[1:], tr.qdd[1:]))
        t0 = parts[-1].t[-1]
    return Trajectory(np.concatenate([p_.t for p_ in parts]), np.vstack([p_.q for p_ in parts]),
                      np.vstack([p_.qd for p_ in parts]), np.vstack([p_.qdd for p_ in parts]), "stop_and_go")


def build_trajectory(scene, solved: list[SolvedStep], planner, task: dict | None = None, alpha: float = 1.0,
                     verbose: bool = True, use_torque: bool = True, extra_payloads=()) -> list[Segment]:
    """planner(scene, step, q_start, q_goal, is_free) -> 관절 경로(list) 를 받아 전체 궤적을 만든다.

    use_torque: 계획 구간의 TOPP-RA에 경사 포락선 토크 제약(0.8 x 한계)을 넣는다.
    alpha: 속도 비율 (1이면 최단시간). 선량 적응 속도는 이후 P 단계에서 구간별로 바꾼다.
    """
    task = task or config.task_config()
    tm, pl = task["timing"], task["planner"]
    r = scene.robot
    vlim, alim = r.vlim, r.alim
    segs, t_now = [], 0.0
    for ss in solved:
        st = ss.step
        apply_state(scene, st.state)
        t0 = time.time()
        if st.kind == "dwell":
            tr = dwell(ss.q_start, tm[st.dwell_key])
            jp = np.vstack([ss.q_start, ss.q_start])
        elif st.kind == "line":
            p0, _ = r.tcp_pose(ss.line_path[0])
            p1, _ = r.tcp_pose(ss.line_path[-1])
            tr = fine_motion(ss.line_path, float(np.linalg.norm(p1 - p0)), tm["fine_speed"], vlim * alpha,
                             alim * alpha ** 2, tm["dt"])
            jp = ss.line_path
        else:
            is_free = make_is_free(scene, st)
            path = planner(scene, st, ss.q_start, ss.q_goal, is_free)
            if path is None:
                raise RuntimeError(f"{st.stage} {st.name}: 경로를 찾지 못했습니다")
            jp = densify(path, pl["densify_step"])
            tq = torque_constraint(scene, st, extra_payloads) if use_torque else None
            tr = topp(jp, vlim, alim, tm["dt"], alpha=alpha, torque=tq)
            for div in (3, 8):
                if _traj_collision_free(scene, st, tr):
                    break
                # 스플라인이 꼭짓점에서 바깥으로 부풀어 충돌하면 점을 더 촘촘히 넣어 경로에 붙인다
                jp = densify(path, pl["densify_step"] / div)
                tr = topp(jp, vlim, alim, tm["dt"], alpha=alpha, torque=tq)
            if not _traj_collision_free(scene, st, tr):
                tr = _stop_and_go(np.asarray(path), vlim * alpha, alim * alpha ** 2, tm["dt"])
                if verbose:
                    print(f"  [참고] {st.name}: 스플라인 궤적이 여유거리를 침범해 꼭짓점마다 정지하는 궤적으로 대체")
        seg = Segment(st, tr.shifted(t_now), np.asarray(jp), time.time() - t0)
        segs.append(seg)
        t_now = seg.traj.t[-1]
        if verbose:
            print(f"  {st.stage} {st.kind:5s} {st.name:16s} {tr.duration:7.2f} s  [{tr.method}]"
                  + (f"  계획 {seg.plan_time:.2f} s" if st.kind == "plan" else ""))
    return segs
