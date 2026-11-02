"""P3 체류 자세 최적화: 계획 구간 목표 자세를 고를 때, 그 뒤 근접 직선 구간과 체류 구간의 부품 선량이 가장 작은 것을 고른다.

배경
- 부품 선량 합의 약 75%가 체류(S2 해제, S5 체결), 22%가 베드 근처 직선 구간에서 나온다 (B0 기준선).
- 체류 중에는 TCP 위치와 공구 축(연직)이 고정되지만 두 자유도가 남는다.
  1) 공구를 베드 축(연직) 둘레로 돌리는 각도 (가정: 원통형 손잡이라 어느 방향에서든 잡을 수 있음)
  2) 7축 로봇의 영공간 (팔꿈치 회전)
- 같은 TCP에서 부품 위치만 바뀌므로 점 로봇(TCP) 선량은 변하지 않는다. 점 로봇 모델로는 이 최적화를 할 수 없다.

방법
- 계획 구간(plan) 목표 후보를 공구 회전각 × 영공간 기준 자세로 많이 만든다 (task.solve_chain의 yaw_offsets, extra_rests).
- 후보마다 뒤따르는 직선 구간을 실제로 풀고(cartesian_line), 직선 구간과 그 끝 체류 구간의 부품 선량을 근사 계산한다.
- 목적함수 J = Σ_k w_k D_k, w_k = 1 / TID_lim,k (J_dose 정의와 같은 꼴. N_ex는 순위에 영향 없음).
- J가 작은 순서로 후보를 돌려주고, solve_chain은 그 순서대로 나머지 작업이 풀리는 첫 후보를 쓴다.
"""
from __future__ import annotations

import numpy as np

from .dose_eval import ComponentDoseEvaluator
from .planning import cartesian_line


def budget_weights(comps, xe_cfg) -> np.ndarray:
    """w_k = RDM / 고장선량_k. 값이 없는 부품(C10)과 기준점(P0)은 0."""
    fail = xe_cfg["budget"]["TID_fail_Gy"]
    rdm = xe_cfg["budget"]["RDM"]
    w = np.zeros(len(comps))
    for k, c in enumerate(comps):
        v = fail.get(c.id)
        if not c.reference and v:
            w[k] = rdm / float(v)
    return w


def make_dwell_ranker(scene, comps, fields, task, weights, keep: int = 8, log: list | None = None):
    """solve_chain(rank=...)에 넘길 함수를 만든다."""
    from .task import apply_state, make_is_free

    ev = ComponentDoseEvaluator(scene.robot, comps)
    v = task["timing"]["fine_speed"]

    def segment_dose(qs, field_name):
        P, tcp, R = ev.positions(qs)
        r = fields[field_name].rate(P, tcp, R, np.zeros(len(qs))) * ev.S[None, :]
        ds = np.linalg.norm(np.diff(tcp, axis=0), axis=1)
        return np.sum(0.5 * (r[1:] + r[:-1]) * (ds / v)[:, None], axis=0) / 3600.0

    def rank(scene_, i, steps, wp, cands, q_cur):
        # i번째 plan 뒤로 line이 이어지다 dwell을 만나는 경우만 다룬다
        j, chain = i + 1, []
        while j < len(steps) and steps[j].kind == "line":
            chain.append(steps[j])
            j += 1
        if not chain or j >= len(steps) or steps[j].kind != "dwell":
            return None
        dw = steps[j]
        T_dw = task["timing"][dw.dwell_key]
        scored = []
        for q0, Rk in cands:
            q, D, ok = q0, np.zeros(len(comps)), True
            for st in chain:
                apply_state(scene_, st.state)
                pos, R = wp[st.goal]
                path = cartesian_line(scene_.robot, q, pos, Rk if Rk is not None else R)
                if path is None:
                    ok = False
                    break
                free = make_is_free(scene_, st)
                if not all(free(path[k]) for k in range(0, len(path), 3)):
                    ok = False
                    break
                D += segment_dose(path, st.field)
                q = path[-1]
            if not ok:
                continue
            apply_state(scene_, dw.state)
            P, tcp, R = ev.positions(q[None, :])
            D += fields[dw.field].rate(P, tcp, R, np.zeros(1))[0] * ev.S * T_dw / 3600.0
            scored.append((float(weights @ D), q0, Rk, D))
        apply_state(scene_, steps[i].state)
        scored.sort(key=lambda s: s[0])
        if log is not None:
            log.append({"plan_step": steps[i].name, "dwell": dw.name, "n_candidates": len(cands),
                        "n_feasible": len(scored), "J": [s[0] for s in scored],
                        "D": [s[3] for s in scored]})
        return [(q0, Rk) for _, q0, Rk, _ in scored[:keep]]

    return rank
