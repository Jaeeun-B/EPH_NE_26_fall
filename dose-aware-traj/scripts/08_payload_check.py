"""가반하중 점검 (10/5 회의 안건): 베드 질량에 따라 경사 포락선에서 토크 제약을 만족하는지.

교체 작업의 운반 자세(웨이포인트)마다, 경사 7개 조건 중 최악 조건의 정적 토크로
(1) 현재 가정 베드 9 kg, (2) ORNL 참고 베드 60 kg 의 토크 사용률과
(3) 토크 상한 0.8 x 한계를 지키는 최대 운반 질량을 구한다.
베드는 TCP 아래에 매달린 점질량 (질량중심 = TCP + 손잡이 + 베드 높이/2).

실행: python scripts/08_payload_check.py
출력: outputs/payload_check.csv, outputs/payload_check.png
"""
import csv

import numpy as np

import _bootstrap  # noqa: F401
from datraj import OUTPUTS, config, viz_style
from datraj.geometry import ship_gravity
from datraj.robot import PointMass
from datraj.scene import Scene
from datraj.task import solve_chain

CARRY_POSES = {
    "들어올림 직후 (Bed A 위)": "들어올림",
    "캐스크 위": "캐스크로 운반",
    "캐스크에 내려놓기": "캐스크에 내려놓기",
    "신규 베드 들어올림": "신규 베드 들어올림",
    "Bed A 자리 위": "Bed A 자리로 운반",
}


def worst_util(robot, q, gvecs, mass, com_off):
    pm = [PointMass("bed", robot.EE_LINK, robot.tcp_local + np.array([0, 0, com_off]), mass)]
    best, joint, case = 0.0, -1, -1
    for ci, g in enumerate(gvecs):
        u = robot.torque_utilization(robot.static_torque(q, g, pm))
        if u.max() > best:
            best, joint, case = float(u.max()), int(np.argmax(u)), ci
    return best, joint, case


def max_mass(robot, q, gvecs, com_off, cap):
    lo, hi = 0.0, 200.0
    if worst_util(robot, q, gvecs, hi, com_off)[0] <= cap:
        return hi
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if worst_util(robot, q, gvecs, mid, com_off)[0] <= cap else (lo, mid)
    return lo


def main():
    params = config.shared_params()
    layout = config.layout()
    scene = Scene()
    robot = scene.robot
    cases = params["inclination_envelope"]["cases"]
    gvecs = [ship_gravity(c["roll_deg"], c["pitch_deg"]) for c in cases]
    cap = robot.tau_cap
    bed = layout["bed_cartridge"]
    off_small = bed["handle_height"] + bed["height"] / 2
    off_ornl = bed["handle_height"] + 0.91 / 2
    m_small = params["payload"]["bed_spent_mass"]
    m_ornl = params["payload"]["reference_ornl_bed_mass"]
    solved = solve_chain(scene, verbose=False)
    by_name = {s.step.name: s for s in solved}
    J = [f"A{i}" for i in range(1, 8)]

    rows = []
    print(f"토크 상한 {cap} x 한계, 경사 {len(cases)}개 조건 중 최악. 베드 질량중심은 TCP 아래 {off_small:.2f} m (ORNL {off_ornl:.3f} m)")
    print(f"{'자세':24s} {'9 kg 사용률':>11s} {'60 kg 사용률':>12s} {'허용 최대 질량':>12s}")
    for label, step_name in CARRY_POSES.items():
        q = by_name[step_name].q_goal
        u9, j9, c9 = worst_util(robot, q, gvecs, m_small, off_small)
        u60, j60, c60 = worst_util(robot, q, gvecs, m_ornl, off_ornl)
        mmax = max_mass(robot, q, gvecs, off_small, cap)
        rows.append({"pose": label, "util_9kg": round(u9, 3), "joint_9kg": J[j9], "case_9kg": cases[c9]["id"],
                     "util_60kg": round(u60, 3), "joint_60kg": J[j60], "case_60kg": cases[c60]["id"],
                     "max_mass_kg": round(mmax, 1)})
        print(f"{label:24s} {u9:7.2f} ({J[j9]}) {u60:8.2f} ({J[j60]}) {mmax:10.1f} kg")
    with open(OUTPUTS / "payload_check.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    worst = min(r["max_mass_kg"] for r in rows)
    print(f"\n운반 자세 전체에서 허용되는 최대 베드 질량: {worst:.1f} kg (공구 1.5 kg 별도)")
    print("ORNL 베드(약 60 kg)는 토크로도, 크기(길이 0.91 m vs 도달거리 0.82 m)로도 이 로봇 범위 밖입니다.")

    viz_style.apply()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8.5, 3.6))
    y = np.arange(len(rows))
    ax.barh(y, [r["max_mass_kg"] for r in rows], color=viz_style.CATEGORICAL[0], height=0.55)
    for yi, r in zip(y, rows):
        ax.text(r["max_mass_kg"], yi, f" {r['max_mass_kg']:.1f} kg", va="center", fontsize=8, color=viz_style.INK_2)
    ax.axvline(m_small, color=viz_style.CATEGORICAL[2], lw=1.4, ls="--")
    ax.text(m_small, -0.6, f" 가정 베드 {m_small:.0f} kg", fontsize=8, color=viz_style.INK_2, va="bottom")
    ax.axvline(m_ornl, color=viz_style.CATEGORICAL[7], lw=1.4, ls="--")
    ax.text(m_ornl, -0.6, f"ORNL 참고 {m_ornl:.0f} kg ", fontsize=8, color=viz_style.INK_2, va="bottom",
            ha="right")
    ax.set_yticks(y, [r["pose"] for r in rows], fontsize=8.5)
    ax.set_ylim(len(rows) - 0.5, -0.9)
    ax.set_xlim(0, m_ornl * 1.12)
    ax.set_xlabel("허용 최대 운반 질량 [kg] (경사 포락선 최악 조건, 토크 0.8 x 한계)")
    ax.set_title("운반 자세별 허용 베드 질량 (KUKA iiwa 14)", loc="left")
    ax.grid(True, axis="x")
    ax.set_axisbelow(True)
    fig.savefig(OUTPUTS / "payload_check.png")
    print(f"그림: {OUTPUTS / 'payload_check.png'}")


if __name__ == "__main__":
    main()
