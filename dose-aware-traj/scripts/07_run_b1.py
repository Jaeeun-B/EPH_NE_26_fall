"""B1 기준선: 엔드이펙터 3D A* (선량 가중 격자) + IK 추종 + TOPP-RA.

이동로봇의 '점 로봇' 선량 경로계획을 그대로 옮긴 비교 기준. TCP 한 점의 선량만 줄이므로
팔의 다른 부품 선량이나 팔 전체의 충돌은 경로를 고를 때 보지 않는다 (추종 단계에서만 확인).
웨이포인트 관절각과 직선·체류 구간은 B0와 같다. 계획 구간만 다르다.

실행: python scripts/07_run_b1.py [--field model|grid] [--N 100]
출력: outputs/b1/ (B0와 같은 형식) + B0 대비 비교표 (outputs/compare_b0_b1.csv)
"""
import argparse
import csv
import json

import numpy as np

import _bootstrap  # noqa: F401
from datraj import OUTPUTS, config, viz
from datraj.astar import make_b1_planner
from datraj.components import load as load_components
from datraj.dose_eval import build_fields
from datraj.results import evaluate, print_summary, save
from datraj.scene import Scene
from datraj.task import build_trajectory, solve_chain


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field", choices=["model", "grid"], default="model")
    ap.add_argument("--N", type=int, default=100)
    args = ap.parse_args()

    task = config.task_config()
    out = OUTPUTS / "b1"
    scene = Scene()
    comps, settings = load_components()
    fields = build_fields(args.field, args.N)
    solved = solve_chain(scene, task)
    notes = []
    print("B1 궤적 생성")
    segs = build_trajectory(scene, solved, make_b1_planner(fields, notes), task)
    for n in notes:
        print("  [참고]", n)
    E = evaluate(segs, scene, fields, comps, settings, label=f"B1 ({args.field})")
    E.summary["notes"] = notes
    save(E, segs, comps, out, "b1")
    print_summary(E, comps)
    viz.trajectory_figures(E, segs, comps, scene, fields, out, "b1")

    b0 = OUTPUTS / "b0" / "summary_b0.json"
    if b0.exists():
        s0 = json.loads(b0.read_text(encoding="utf-8"))
        s1 = E.summary
        rows = []
        for cid in s1["dose_total_Gy"]:
            d0, d1 = s0["dose_total_Gy"][cid], s1["dose_total_Gy"][cid]
            rows.append({"id": cid, "D_b0_mGy": round(d0 * 1e3, 4), "D_b1_mGy": round(d1 * 1e3, 4),
                         "change_pct": round((d1 / d0 - 1) * 100, 2)})
        moving = lambda s: sum(v for st, d in s["dose_stage_Gy"].items() if st in ("S1", "S3", "S4", "S6")  # noqa: E731
                               for cid, v in d.items() if cid != "P0")
        with open(OUTPUTS / "compare_b0_b1.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
        print("\nB0 대비 B1 (이동 구간 S1·S3·S4·S6 부품 선량 합)")
        print(f"  B0 {moving(s0) * 1e3:.2f} mGy -> B1 {moving(s1) * 1e3:.2f} mGy "
              f"({(moving(s1) / moving(s0) - 1) * 100:+.1f}%), 동작시간 {s0['T_motion_s']:.1f} -> {s1['T_motion_s']:.1f} s")
        print(f"  TCP(점 로봇) {s0['point_robot_TCP_dose_Gy'] * 1e3:.2f} -> {s1['point_robot_TCP_dose_Gy'] * 1e3:.2f} mGy")
        print(f"  비교표: {OUTPUTS / 'compare_b0_b1.csv'}")


if __name__ == "__main__":
    main()
