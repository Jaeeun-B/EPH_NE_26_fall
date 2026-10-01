"""B0 기준선: RRT-Connect + 경로 단축 + TOPP-RA (선량을 보지 않는 시간 최소 궤적).

S1~S6 전체 교체 작업을 계획하고, 부품별 누적선량과 경사 포락선 토크를 평가한다.

실행: python scripts/06_run_b0.py [--field model|grid] [--N 100] [--gui]
  --field model : 가상 선원 해석식으로 선량 계산 (기본, 격자 보간 오차 없음)
  --field grid  : data/dose_grids 의 격자 사용 (방사선 파트 격자를 넣으면 이 경로로 계산)
출력: outputs/b0/ traj_b0.csv, traj_b0_A2A4.csv, dose_by_component_b0.csv, summary_b0.json, 그림
"""
import argparse
import time

import numpy as np

import _bootstrap  # noqa: F401
from datraj import OUTPUTS, config
from datraj.components import load as load_components
from datraj.dose_eval import build_fields
from datraj.planning import make_rrt_planner
from datraj.results import evaluate, print_summary, save
from datraj.scene import Scene
from datraj.task import build_trajectory, solve_chain
from datraj import viz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field", choices=["model", "grid"], default="model")
    ap.add_argument("--N", type=int, default=100)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--gui", action="store_true", help="계산 후 PyBullet 창에서 재생")
    ap.add_argument("--speed", type=float, default=1.0, help="재생 배속 (--gui와 함께)")
    args = ap.parse_args()

    task = config.task_config()
    if args.seed is not None:
        task["planner"]["seed"] = args.seed
    out = OUTPUTS / "b0"
    scene = Scene()
    comps, settings = load_components()
    fields = build_fields(args.field, args.N)

    t0 = time.time()
    solved = solve_chain(scene, task)
    print("B0 궤적 생성")
    segs = build_trajectory(scene, solved, make_rrt_planner(task), task)
    print(f"계획 완료 {time.time() - t0:.1f} s. 선량·토크 평가 중...")
    E = evaluate(segs, scene, fields, comps, settings, label=f"B0 ({args.field})")
    save(E, segs, comps, out, "b0")
    print_summary(E, comps)
    viz.trajectory_figures(E, segs, comps, scene, fields, out, "b0")
    print(f"\n출력 폴더: {out}")
    if args.gui:
        scene.disconnect()
        viz.replay_gui(E, segs, fields, speed=args.speed)


if __name__ == "__main__":
    main()
