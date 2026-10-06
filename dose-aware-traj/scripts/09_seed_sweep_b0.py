"""B0 RRT 시드 민감도: 여러 시드로 B0를 돌려 B1과의 차이가 시드 탓인지 본다.

B0 기본 결과(seed 1)는 S4 "Bed A 자리로 운반"에서 TCP가 높이 올라가는 우회를 만든다.
B1과의 계획 구간 선량·동작시간·토크 차이가 이 우회 하나에서 나오는지, 다른 시드의 B0와
비교해도 남는지 확인한다. outputs/b0 의 기본 결과는 건드리지 않는다.

실행: python scripts/09_seed_sweep_b0.py [--seeds 1-30] [--field model|grid] [--N 100]
전제: 07_run_b1.py (outputs/b1/summary_b1.json 과 비교)
출력: outputs/b0_seeds/seed_sweep.csv
"""
import argparse
import csv
import json
import time

import numpy as np

import _bootstrap  # noqa: F401
from datraj import OUTPUTS, config
from datraj.components import load as load_components
from datraj.dose_eval import build_fields
from datraj.planning import make_rrt_planner
from datraj.results import evaluate
from datraj.scene import Scene
from datraj.task import build_trajectory, solve_chain


def parse_seeds(s):
    if "-" in s:
        a, b = s.split("-")
        return list(range(int(a), int(b) + 1))
    return [int(x) for x in s.split(",")]


def plan_rows(summary, E, segs, scene):
    """계획 구간별 부품 선량 합 [mGy], 시간 [s], 최대 토크 사용률, TCP 최고 높이 [m]."""
    rows = []
    for i, (seg, sr) in enumerate(zip(segs, summary["segments"])):
        if seg.step.kind != "plan":
            continue
        u = E.util_env[E.seg_index == i]
        u = u[~np.isnan(u)]
        z = float(max(scene.robot.tcp_pose(q)[0][2] for q in seg.traj.q[::10]))
        rows.append({"name": f"{seg.step.stage} {seg.step.name}", "dose_mGy": sr["dose_sum_components_Gy"] * 1e3,
                     "T_s": seg.traj.duration, "util": float(u.max()) if len(u) else np.nan, "z_max_m": z})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="1-30")
    ap.add_argument("--field", choices=["model", "grid"], default="model")
    ap.add_argument("--N", type=int, default=100)
    args = ap.parse_args()

    out = OUTPUTS / "b0_seeds"
    out.mkdir(parents=True, exist_ok=True)
    scene = Scene()
    comps, settings = load_components()
    fields = build_fields(args.field, args.N)
    task = config.task_config()
    solved = solve_chain(scene, task)

    table = []
    for seed in parse_seeds(args.seeds):
        task["planner"]["seed"] = seed
        t0 = time.time()
        segs = build_trajectory(scene, solved, make_rrt_planner(task), task, verbose=False)
        E = evaluate(segs, scene, fields, comps, settings, label=f"B0 seed {seed}")
        s = E.summary
        pr = plan_rows(s, E, segs, scene)
        row = {"seed": seed, "T_motion_s": s["T_motion_s"], "util_max": s["max_torque_utilization_envelope"],
               "clear_min_m": s["min_clearance_plan_m"], "plan_dose_mGy": sum(p["dose_mGy"] for p in pr),
               "sum_dose_mGy": s["sum_dose_components_Gy"] * 1e3}
        for k, p in enumerate(pr):
            row[f"P{k + 1}_dose_mGy"] = p["dose_mGy"]
            row[f"P{k + 1}_T_s"] = p["T_s"]
            row[f"P{k + 1}_util"] = p["util"]
            row[f"P{k + 1}_zmax_m"] = p["z_max_m"]
        table.append(row)
        print(f"seed {seed:3d}: 동작 {row['T_motion_s']:6.1f} s, 토크 {row['util_max']:.3f}, "
              f"계획 구간 선량 {row['plan_dose_mGy']:6.2f} mGy, "
              f"구간별 z_max [m] {[round(p['z_max_m'], 2) for p in pr]}  ({time.time() - t0:.0f} s)")
    names = [p["name"] for p in pr]

    with open(out / "seed_sweep.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=table[0].keys())
        w.writeheader()
        w.writerows(table)

    print("\n계획 구간: " + ", ".join(f"P{k + 1} = {n}" for k, n in enumerate(names)))
    b1 = OUTPUTS / "b1" / "summary_b1.json"
    if not b1.exists():
        print("B1 결과 없음: 07_run_b1.py 먼저 실행")
        return
    s1 = json.loads(b1.read_text(encoding="utf-8"))
    p1 = [sr["dose_sum_components_Gy"] * 1e3 for sr in s1["segments"] if sr["kind"] == "plan"]
    print(f"\nB0 시드 {len(table)}개 대비 B1 (가상 선원, 상대 비교용)")
    print(f"{'항목':24s} {'B0 최소':>9s} {'B0 중앙':>9s} {'B0 최대':>9s} {'B1':>9s}")

    def line(label, vals, b1v):
        print(f"{label:24s} {np.min(vals):9.3f} {np.median(vals):9.3f} {np.max(vals):9.3f} {b1v:9.3f}")

    line("동작시간 [s]", [r["T_motion_s"] for r in table], s1["T_motion_s"])
    line("토크 사용률", [r["util_max"] for r in table], s1["max_torque_utilization_envelope"])
    line("계획 구간 선량 [mGy]", [r["plan_dose_mGy"] for r in table], sum(p1))
    for k, n in enumerate(names):
        line(f"  P{k + 1} 선량 [mGy]", [r[f"P{k + 1}_dose_mGy"] for r in table], p1[k])
    print(f"\n저장: {out / 'seed_sweep.csv'}")


if __name__ == "__main__":
    main()
