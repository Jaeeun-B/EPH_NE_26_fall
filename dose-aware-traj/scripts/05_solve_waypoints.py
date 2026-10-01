"""S1~S6 작업 자세: 단계별 시작·끝 TCP 자세를 정하고 IK로 관절각을 구한다.

모든 계획기(B0, B1, 이후 P1~P3)가 같은 웨이포인트 관절각에서 출발하도록 저장해 둔다.
실행: python scripts/05_solve_waypoints.py
출력: outputs/waypoints.json, outputs/scene/wp_*.png (주요 자세 그림)
"""
import json

import numpy as np

import _bootstrap  # noqa: F401
from datraj import OUTPUTS
from datraj.scene import Scene
from datraj.task import STAGE_NAMES, apply_state, solve_chain


def main():
    scene = Scene()
    solved = solve_chain(scene)
    rows = []
    print(f"\n{'단계':10s} {'종류':6s} {'구간':18s} {'TCP 목표 [m]':24s} {'관절 한계 여유 [rad]':>16s} {'여유거리 [m]':>10s}")
    for s in solved:
        apply_state(scene, s.step.state)
        tcp, R = scene.robot.tcp_pose(s.q_goal)
        r = scene.robot
        margin = float(np.min(np.minimum(s.q_goal - r.lower, r.upper - s.q_goal)))
        clear = scene.min_clearance(s.q_goal)
        rows.append({"stage": s.step.stage, "kind": s.step.kind, "name": s.step.name, "state": s.step.state,
                     "q_goal": np.round(s.q_goal, 6).tolist(), "tcp": np.round(tcp, 4).tolist(),
                     "joint_limit_margin": round(margin, 4), "clearance": round(clear, 4)})
        print(f"{s.step.stage} {STAGE_NAMES[s.step.stage]:6s} {s.step.kind:6s} {s.step.name:16s} "
              f"{str(np.round(tcp, 3).tolist()):24s} {margin:14.3f} {clear:12.3f}")
    (OUTPUTS).mkdir(exist_ok=True)
    with open(OUTPUTS / "waypoints.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    out = OUTPUTS / "scene"
    out.mkdir(parents=True, exist_ok=True)
    for name, key in (("S2_release", "커플링 해제·파지"), ("S3_carry", "캐스크로 운반"), ("S4_pick", "파지")):
        s = next(x for x in solved if x.step.name == key)
        apply_state(scene, s.step.state)
        scene.snapshot(out / f"wp_{name}.png", s.q_goal, yaw=215, pitch=-25, dist=1.9)
    print(f"\n저장: {OUTPUTS / 'waypoints.json'}, 자세 그림 {out}/wp_*.png")


if __name__ == "__main__":
    main()
