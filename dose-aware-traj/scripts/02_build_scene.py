"""PyBullet 핫셀 장면 확인: 배치도로 장애물 생성, 로봇 로드, 경사 중력, 장면 그림.

실행: python scripts/02_build_scene.py          (그림만 저장)
      python scripts/02_build_scene.py --gui    (PyBullet 창으로 보기, 창을 닫으면 종료)
출력: outputs/scene/scene_*.png
"""
import argparse
import time

import numpy as np
import pybullet as p

import _bootstrap  # noqa: F401
from datraj import OUTPUTS, config
from datraj.geometry import ship_gravity
from datraj.scene import Scene


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gui", action="store_true")
    args = ap.parse_args()

    layout = config.layout()
    task = config.task_config()
    scene = Scene(gui=args.gui)
    r = scene.robot
    q_home = np.asarray(task["home_q"])
    print(f"배치도 {layout['layout_version']}: 장애물 {len(scene.env_links) + 1 + len(scene.walls)}개, "
          f"로봇 {r.N}축, 여유거리 {scene.margin:.3f} m")
    tcp, _ = r.tcp_pose(q_home)
    print(f"대기 자세 TCP {np.round(tcp, 3).tolist()}, 충돌 {scene.in_collision(q_home)}, "
          f"최소 여유거리 {scene.min_clearance(q_home):.3f} m")

    print("\n경사 조건별 중력 벡터와 대기 자세 정적 토크 사용률 (공구 포함)")
    for c in scene.params["inclination_envelope"]["cases"]:
        g = ship_gravity(c["roll_deg"], c["pitch_deg"])
        u = r.torque_utilization(r.static_torque(q_home, g))
        print(f"  {c['id']:12s} roll {c['roll_deg']:6.1f}°, pitch {c['pitch_deg']:5.1f}°  "
              f"g = [{g[0]:6.2f}, {g[1]:6.2f}, {g[2]:6.2f}]  최대 사용률 {u.max():.2f} (A{int(np.argmax(u)) + 1})")

    out = OUTPUTS / "scene"
    out.mkdir(parents=True, exist_ok=True)
    views = {"front_left": (35, -28), "front_right": (-35, -28), "top": (0, -80)}
    for name, (yaw, pitch) in views.items():
        scene.snapshot(out / f"scene_{name}.png", q_home, yaw=yaw + 180, pitch=pitch)
    print(f"\n장면 그림: {out}")

    if args.gui:
        print("PyBullet 창을 닫으면 종료합니다.")
        r.set_q(q_home)
        scene.update_attached(q_home)
        L = 0.3
        for axis, col in ((0, [1, 0, 0]), (1, [0, 0.6, 0]), (2, [0, 0, 1])):
            e = np.zeros(3)
            e[axis] = L
            p.addUserDebugLine([0, 0, 0.002], (e + [0, 0, 0.002]).tolist(), col, 3, physicsClientId=scene.cid)
        p.addUserDebugText("x", [L + 0.03, 0, 0], [1, 0, 0], physicsClientId=scene.cid)
        p.addUserDebugText("y", [0, L + 0.03, 0], [0, 0.6, 0], physicsClientId=scene.cid)
        try:
            while p.isConnected(scene.cid):
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
