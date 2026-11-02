"""P3: 체류 자세 최적화 (B0 경로계획 그대로, 계획 구간 목표 자세만 부품 선량 기준으로 고름).

B0와 같은 RRT-Connect + 경로 단축 + TOPP-RA를 쓰고, 다른 점은 웨이포인트 관절각을 고르는 방식 하나뿐이다.
- B0: 관절 한계 여유와 여유거리 점수로 목표 자세를 고름 (선량을 보지 않음)
- P3: 공구 회전각 24개(15° 간격) × 영공간 기준 자세 21개 후보 중, 뒤따르는 근접 직선 구간과 체류 구간의
      부품 선량 가중합 J = Σ D_k / TID_lim,k 가 가장 작고 나머지 작업이 풀리는 자세를 고름 (datraj/posture.py)

가정: 그리퍼가 원통형 손잡이를 감싸는 구조라 베드 축 둘레 어느 각도에서든 잡을 수 있다.
(B0도 공구 회전 0°, ±90° 후보를 이미 쓰고 있어 같은 가정 위에 있다.)

실행: python scripts/13_dwell_posture_opt.py        (06을 먼저 돌려 outputs/b0가 있어야 비교표가 나옴)
출력: outputs/p3/ traj_p3.csv, dose_by_component_p3.csv, summary_p3.json, 그림
      outputs/compare_b0_p3.csv
"""
import csv
import json
import time

import numpy as np

import _bootstrap  # noqa: F401
from datraj import OUTPUTS, config, viz
from datraj import xe_bed as X
from datraj.components import load as load_components
from datraj.dose_eval import build_fields
from datraj.planning import make_rrt_planner
from datraj.posture import budget_weights, make_dwell_ranker
from datraj.results import evaluate, print_summary, save
from datraj.scene import Scene
from datraj.task import build_trajectory, solve_chain

YAWS = np.deg2rad(np.arange(-180, 180, 15))
A3_VALUES = (-1.0, -0.5, 0.5, 1.0)


def main():
    task = config.task_config()
    scene = Scene()
    comps, settings = load_components()
    fields = build_fields("model")
    w = budget_weights(comps, X.load())

    extra = []
    for r in task["ik_rest_candidates"]:
        for a3 in A3_VALUES:
            rr = list(r)
            rr[2] = a3
            extra.append(rr)

    log = []
    rank = make_dwell_ranker(scene, comps, fields, task, w, log=log)
    t0 = time.time()
    solved = solve_chain(scene, task, rank=rank, yaw_offsets=tuple(YAWS), extra_rests=extra)
    print(f"P3 웨이포인트 선택 {time.time() - t0:.1f} s")
    for e in log:
        J = e["J"]
        print(f"  {e['plan_step']:14s} -> {e['dwell']:10s}: 후보 {e['n_candidates']}개 중 직선·체류 가능 {e['n_feasible']}개, "
              f"J 최소 {min(J):.4g} / 중앙 {np.median(J):.4g} / 최대 {max(J):.4g}" if J else "  (가능한 후보 없음)")

    print("P3 궤적 생성 (B0와 같은 RRT 시드)")
    segs = build_trajectory(scene, solved, make_rrt_planner(task), task)
    E = evaluate(segs, scene, fields, comps, settings, label="P3 (model)")
    out = OUTPUTS / "p3"
    save(E, segs, comps, out, "p3")
    print_summary(E, comps)
    viz.trajectory_figures(E, segs, comps, scene, fields, out, "p3")

    real = [k for k, c in enumerate(comps) if not c.reference]
    tcp_k = next(k for k, c in enumerate(comps) if c.reference)
    J_p3 = float(w @ E.dose_total)
    summ = E.summary
    summ["J_weighted"] = J_p3
    summ["weights_note"] = "w_k = RDM / 고장선량_k (config/xe_bed.json). C10, P0는 0"
    with open(out / "summary_p3.json", "w", encoding="utf-8") as f:
        json.dump(summ, f, ensure_ascii=False, indent=2)
    with open(out / "candidate_log.json", "w", encoding="utf-8") as f:
        json.dump([{k: (v if k != "D" else [list(map(float, d)) for d in v]) for k, v in e.items()} for e in log],
                  f, ensure_ascii=False, indent=1)

    b0 = OUTPUTS / "b0" / "dose_by_component_b0.csv"
    if not b0.exists():
        print("outputs/b0가 없어 비교표를 만들지 않습니다 (06 먼저 실행)")
        return
    with open(b0, encoding="utf-8") as f:
        D0 = {r["id"]: float(r["D_total_Gy"]) for r in csv.DictReader(f)}
    S0 = json.load(open(OUTPUTS / "b0" / "summary_b0.json", encoding="utf-8"))
    d0 = np.array([D0[c.id] for c in comps])
    J_b0 = float(w @ d0)
    rows = []
    for k, c in enumerate(comps):
        rows.append({"id": c.id, "name": c.name, "B0_Gy": d0[k], "P3_Gy": float(E.dose_total[k]),
                     "change_pct": (E.dose_total[k] / d0[k] - 1) * 100, "weight": w[k]})
    with open(OUTPUTS / "compare_b0_p3.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)

    print("\nB0 대비 P3 (작업 전체, 가상 선원)")
    print("부품    이름              B0 [mGy]   P3 [mGy]   변화")
    for r in rows:
        print(f"{r['id']:5s} {r['name']:14s} {r['B0_Gy'] * 1e3:9.1f} {r['P3_Gy'] * 1e3:9.1f}  {r['change_pct']:+6.1f}%")
    sum0, sum3 = d0[real].sum(), E.dose_total[real].sum()
    print(f"부품 선량 합: {sum0 * 1e3:.1f} -> {sum3 * 1e3:.1f} mGy ({(sum3 / sum0 - 1) * 100:+.1f}%)")
    print(f"가중 J (Σ D_k / TID_lim,k): {J_b0:.4e} -> {J_p3:.4e} ({(J_p3 / J_b0 - 1) * 100:+.1f}%)")
    print(f"TCP(점 로봇): {d0[tcp_k] * 1e3:.1f} -> {E.dose_total[tcp_k] * 1e3:.1f} mGy "
          f"({(E.dose_total[tcp_k] / d0[tcp_k] - 1) * 100:+.1f}%)")
    print(f"작업시간 {S0['T_total_s']:.1f} -> {summ['T_total_s']:.1f} s, 토크 사용률 {S0['max_torque_utilization_envelope']:.3f} -> "
          f"{summ['max_torque_utilization_envelope']:.3f}, 최소 여유거리 {S0['min_clearance_plan_m']:.3f} -> {summ['min_clearance_plan_m']:.3f} m")
    print(f"\n출력 폴더: {out}")


if __name__ == "__main__":
    main()
