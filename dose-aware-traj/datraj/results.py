"""궤적 평가(선량, 토크, 지표)와 저장."""
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import config
from .components import Component, budgets
from .dose_eval import ComponentDoseEvaluator
from .geometry import ship_gravity
from .robot import PointMass
from .task import STAGE_NAMES, STAGES, Segment, payloads_for


@dataclass
class Evaluation:
    t: np.ndarray            # (T,)
    q: np.ndarray            # (T, 7)
    qd: np.ndarray
    qdd: np.ndarray
    stage: list              # (T,)
    seg_index: np.ndarray    # (T,)
    rates: np.ndarray        # (T, K) Gy/h (투과율 적용)
    dose_stage: dict         # stage -> (K,) Gy
    dose_total: np.ndarray   # (K,)
    tau_level: np.ndarray    # (T, 7) 경사 0도
    util_env: np.ndarray     # (T,) 경사 포락선 내 최대 토크 사용률 (서브샘플 위치 외에는 nan)
    util_joint: np.ndarray   # (T,) 최대 사용률 관절
    summary: dict
    seg_dose: np.ndarray = None  # (구간 수, K) Gy


def shield_payloads(comps: list[Component], robot) -> list[PointMass]:
    return [PointMass(f"shield_{c.id}", c.link, c.offset, c.shield_mass)
            for c in comps if c.shield_mass > 0 and c.link >= 0]


def evaluate(segments: list[Segment], scene, fields: dict, comps: list[Component], settings: dict,
             torque_every: int = 5, label: str = "") -> Evaluation:
    robot = scene.robot
    params = scene.params
    ev = ComponentDoseEvaluator(robot, comps)
    cases = params["inclination_envelope"]["cases"]
    gvecs = [ship_gravity(c["roll_deg"], c["pitch_deg"]) for c in cases]
    shields = shield_payloads(comps, robot)

    ts, qs, qds, qdds, stages, segi, rates = [], [], [], [], [], [], []
    dose_stage = {s: np.zeros(len(comps)) for s in STAGES}
    tau_l, util, ujoint = [], [], []
    seg_dose = []
    for i, seg in enumerate(segments):
        tr = seg.traj
        res = ev.evaluate(tr.t, tr.q, fields[seg.step.field])
        dose_stage[seg.step.stage] += res.dose
        seg_dose.append(res.dose)
        pl = payloads_for(seg.step, robot, params) + shields
        n = len(tr.t)
        tl = np.full((n, 7), np.nan)
        ut = np.full(n, np.nan)
        uj = np.full(n, -1)
        every = 1 if seg.step.kind == "dwell" else torque_every
        idx = sorted(set(range(0, n, every)) | {n - 1})
        for k in idx:
            best = 0.0
            for gi, g in enumerate(gvecs):
                tau = robot.inverse_dynamics(tr.q[k], tr.qd[k], tr.qdd[k], g, pl)
                if gi == 0:
                    tl[k] = tau
                u = robot.torque_utilization(tau)
                if u.max() > best:
                    best, uj[k] = float(u.max()), int(np.argmax(u))
            ut[k] = best
        sl = slice(1, None) if i > 0 else slice(None)   # 구간 경계의 중복 시점 제거
        ts.append(tr.t[sl]); qs.append(tr.q[sl]); qds.append(tr.qd[sl]); qdds.append(tr.qdd[sl])
        stages += [seg.step.stage] * len(tr.t[sl]); segi.append(np.full(len(tr.t[sl]), i))
        rates.append(res.rates[sl]); tau_l.append(tl[sl]); util.append(ut[sl]); ujoint.append(uj[sl])

    E = Evaluation(np.concatenate(ts), np.vstack(qs), np.vstack(qds), np.vstack(qdds), stages,
                   np.concatenate(segi), np.vstack(rates), dose_stage,
                   sum(dose_stage.values()), np.vstack(tau_l), np.concatenate(util), np.concatenate(ujoint), {})
    E.seg_dose = np.asarray(seg_dose)
    E.summary = summarize(E, segments, comps, settings, scene, label)
    return E


def _jerk_integral(segments) -> float:
    total = 0.0
    for seg in segments:
        tr = seg.traj
        if len(tr.t) < 3 or seg.step.kind == "dwell":
            continue
        j = np.gradient(tr.qdd, tr.t, axis=0)
        total += float(np.trapezoid(np.sum(j ** 2, axis=1), tr.t))
    return total


def summarize(E: Evaluation, segments, comps, settings, scene, label) -> dict:
    real = [k for k, c in enumerate(comps) if not c.reference]
    B = budgets(comps, settings.get("N_ex"))
    usage = E.dose_total / B
    have_budget = not np.all(np.isnan(usage[real]))
    stage_time = {s: 0.0 for s in STAGES}
    motion_time = 0.0
    for seg in segments:
        stage_time[seg.step.stage] += seg.traj.duration
        if seg.step.kind != "dwell":
            motion_time += seg.traj.duration
    tcp_k = next((k for k, c in enumerate(comps) if c.reference), None)
    kmax = real[int(np.argmax(E.dose_total[real]))]
    max_rate = np.max(E.rates[:, real], axis=0)
    util = E.util_env[~np.isnan(E.util_env)]
    clear = []
    for seg in segments:
        if seg.step.kind == "plan":
            from .task import apply_state
            apply_state(scene, seg.step.state)
            for k in range(0, len(seg.traj.q), 10):
                clear.append(scene.min_clearance(seg.traj.q[k]))
    by_kind = {"plan": 0.0, "line": 0.0, "dwell": 0.0}
    seg_rows = []
    for seg, d in zip(segments, E.seg_dose):
        by_kind[seg.step.kind] += float(np.sum(d[real]))
        seg_rows.append({"stage": seg.step.stage, "kind": seg.step.kind, "name": seg.step.name,
                         "duration_s": round(seg.traj.duration, 3), "dose_sum_components_Gy": float(np.sum(d[real])),
                         "dose_TCP_Gy": float(d[tcp_k]) if tcp_k is not None else None})
    tot = sum(by_kind.values())
    return {
        "label": label,
        "dose_share_by_kind": {k: round(v / tot, 4) for k, v in by_kind.items()},
        "segments": seg_rows,
        "T_total_s": round(float(E.t[-1] - E.t[0]), 3),
        "T_motion_s": round(motion_time, 3),
        "stage_time_s": {s: round(v, 3) for s, v in stage_time.items()},
        "dose_total_Gy": {comps[k].id: float(E.dose_total[k]) for k in range(len(comps))},
        "dose_stage_Gy": {s: {comps[k].id: float(v[k]) for k in range(len(comps))} for s, v in E.dose_stage.items()},
        "sum_dose_components_Gy": float(np.sum(E.dose_total[real])),
        "max_component": {"id": comps[kmax].id, "name": comps[kmax].name, "dose_Gy": float(E.dose_total[kmax])},
        "point_robot_TCP_dose_Gy": float(E.dose_total[tcp_k]) if tcp_k is not None else None,
        "J_dose": float(np.nansum(usage[real])) if have_budget else None,
        "max_budget_usage": float(np.nanmax(usage[real])) if have_budget else None,
        "budget_note": None if have_budget else "TID_max, N_ex 미입력: 소재 파트 회신 후 계산",
        "max_dose_rate_Gy_h": {comps[k].id: float(max_rate[i]) for i, k in enumerate(real)},
        "jerk_integral": _jerk_integral(segments),
        "max_torque_utilization_envelope": float(util.max()) if len(util) else None,
        "torque_cap": scene.robot.tau_cap,
        "torque_ok": bool(util.max() <= scene.robot.tau_cap) if len(util) else None,
        "min_clearance_plan_m": float(min(clear)) if clear else None,
        "planning_time_s": round(sum(s.plan_time for s in segments if s.step.kind == "plan"), 2),
        "timing_methods": sorted({s.traj.method for s in segments}),
    }


def save(E: Evaluation, segments, comps, out_dir: Path, tag: str) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    J = [f"A{i}" for i in range(1, 8)]
    # 전체 궤적 (제어 파트 입력용)
    with open(out_dir / f"traj_{tag}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "stage", "segment", "kind", "carrying"] + [f"q_{j}" for j in J] + [f"qd_{j}" for j in J]
                   + [f"qdd_{j}" for j in J] + [f"tau_{j}" for j in J] + ["util_envelope_max"])
        for k in range(len(E.t)):
            st = segments[E.seg_index[k]].step
            w.writerow([f"{E.t[k]:.4f}", E.stage[k], int(E.seg_index[k]), st.kind, st.carrying or ""]
                       + [f"{v:.6f}" for v in E.q[k]] + [f"{v:.6f}" for v in E.qd[k]] + [f"{v:.6f}" for v in E.qdd[k]]
                       + ["" if np.isnan(v) else f"{v:.4f}" for v in E.tau_level[k]]
                       + ["" if np.isnan(E.util_env[k]) else f"{E.util_env[k]:.4f}"])
    # A2, A4만 (Simscape 2관절 모델용)
    with open(out_dir / f"traj_{tag}_A2A4.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "stage", "carrying", "q_A2", "q_A4", "qd_A2", "qd_A4", "qdd_A2", "qdd_A4", "tau_A2", "tau_A4"])
        for k in range(len(E.t)):
            st = segments[E.seg_index[k]].step
            tl = E.tau_level[k]
            w.writerow([f"{E.t[k]:.4f}", E.stage[k], st.carrying or "", f"{E.q[k, 1]:.6f}", f"{E.q[k, 3]:.6f}",
                        f"{E.qd[k, 1]:.6f}", f"{E.qd[k, 3]:.6f}", f"{E.qdd[k, 1]:.6f}", f"{E.qdd[k, 3]:.6f}",
                        "" if np.isnan(tl[1]) else f"{tl[1]:.4f}", "" if np.isnan(tl[3]) else f"{tl[3]:.4f}"])
    # 부품별 선량 (소재 파트 검토용)
    with open(out_dir / f"dose_by_component_{tag}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "name"] + [f"D_{s}_Gy" for s in STAGES] + ["D_total_Gy", "S_k", "TID_max_Gy", "max_rate_Gy_h"])
        for k, c in enumerate(comps):
            w.writerow([c.id, c.name] + [f"{E.dose_stage[s][k]:.6e}" for s in STAGES] + [f"{E.dose_total[k]:.6e}",
                       f"{c.S:.4f}", "" if math.isnan(c.tid_max) else c.tid_max, f"{np.max(E.rates[:, k]):.4e}"])
    with open(out_dir / f"summary_{tag}.json", "w", encoding="utf-8") as f:
        json.dump(E.summary, f, ensure_ascii=False, indent=2)


def print_summary(E: Evaluation, comps) -> None:
    s = E.summary
    print(f"\n[{s['label']}] 총 작업시간 {s['T_total_s']:.1f} s (동작 {s['T_motion_s']:.1f} s)")
    print("  단계별 시간: " + ", ".join(f"{k} {STAGE_NAMES[k]} {v:.1f}s" for k, v in s["stage_time_s"].items()))
    print(f"  최대 선량 부품: {s['max_component']['id']} {s['max_component']['name']} "
          f"{s['max_component']['dose_Gy'] * 1e3:.3f} mGy  |  점 로봇(TCP) {s['point_robot_TCP_dose_Gy'] * 1e3:.3f} mGy")
    print(f"  경사 포락선 최대 토크 사용률: {s['max_torque_utilization_envelope']:.2f} (상한 {s['torque_cap']})"
          f"  |  최소 여유거리(계획 구간): {s['min_clearance_plan_m']:.3f} m")
    if not s["torque_ok"]:
        print("  [주의] 토크 상한 초과. toppra가 없으면 토크 제약 없이 시간 매개변수화되므로 SETUP.md 4-1을 참고해 설치하세요.")
    sh = s["dose_share_by_kind"]
    print(f"  부품 선량 합의 구성: 체류 {sh['dwell'] * 100:.0f}%, 접촉 근처 직선 {sh['line'] * 100:.0f}%, "
          f"경로계획 구간 {sh['plan'] * 100:.0f}%")
    print("  단계별 선량 합 [mGy] (TCP 제외): " + ", ".join(
        f"{st} {sum(v for cid, v in d.items() if cid != 'P0') * 1e3:.2f}" for st, d in s["dose_stage_Gy"].items()))
