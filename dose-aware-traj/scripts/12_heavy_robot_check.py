"""대형 로봇(KUKA KR 120/210/300 R2700-2)의 경사 포락선 허용 하중 점검.

08_payload_check.py와 같은 방식(준정적 중력 경사, 토크 상한 0.8 × effort)으로,
작업 공간 안의 대표 자세 격자에서 플랜지에 매달 수 있는 최대 질량을 구한다.

모델은 저장소에 넣지 않는다(메시 용량). 처음 한 번 받으세요:
  git clone --depth 1 https://github.com/kroshu/kuka_robot_descriptions data/robots/kuka_robot_descriptions

실행: python scripts/12_heavy_robot_check.py
출력: outputs/heavy_robot/heavy_payload.csv, summary_heavy_robot.json
"""
import csv
import json

import numpy as np
import pybullet as p

import _bootstrap  # noqa: F401
from datraj import OUTPUTS, config
from datraj.geometry import ship_gravity
from datraj.robot_kr import KRRobot, MODELS

RADII = [1.2, 1.6, 2.0, 2.4]      # 베이스 축에서 플랜지까지 수평거리 [m]
HEIGHTS = [0.2, 0.7, 1.2]         # 베이스 설치면 기준 플랜지 높이 [m]
COM_OFFSETS = [0.3, 0.6]          # 플랜지 아래 모듈 질량중심까지 [m]
RATED = {"kr120": 120.0, "kr210": 210.0, "kr300": 300.0}   # 제조사 정격 가반하중 [kg]


def max_mass(robot, q, gvecs, d, cap, hi=2000.0):
    off = np.array([0.0, 0.0, -d])

    def util(m):
        return max(float(np.max(np.abs(robot.static_torque(q, g, m, off)) / robot.tau_max)) for g in gvecs)

    def limiting_joint(m):
        best, jb = 0.0, -1
        for g in gvecs:
            u = np.abs(robot.static_torque(q, g, m, off)) / robot.tau_max
            if u.max() > best:
                best, jb = float(u.max()), int(np.argmax(u))
        return jb

    if util(0.0) > cap:
        return 0.0, util(0.0), limiting_joint(0.0)
    if util(hi) <= cap:
        return hi, util(0.0), -1
    lo = 0.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if util(mid) <= cap else (lo, mid)
    return lo, util(0.0), limiting_joint(lo)


def main():
    params = config.shared_params()
    cap = float(params["robot"].get("torque_utilization_cap", 0.8)) if "robot" in params else 0.8
    cases = params["inclination_envelope"]["cases"]
    gvecs = [ship_gravity(c["roll_deg"], c["pitch_deg"]) for c in cases]
    out = OUTPUTS / "heavy_robot"
    out.mkdir(parents=True, exist_ok=True)
    cid = p.connect(p.DIRECT)
    rows, summ = [], {"torque_cap": cap, "n_cases": len(cases), "models": {}}
    down = p.getQuaternionFromEuler([np.pi, 0, 0])
    for model in MODELS:
        robot = KRRobot(model, cid)
        masses = []
        for r in RADII:
            for z in HEIGHTS:
                q, err = robot.ik([r, 0.0, z], down)
                if err > 0.01:
                    rows.append({"model": model, "r_m": r, "z_m": z, "com_offset_m": None, "ik_err_m": round(err, 4),
                                 "max_mass_kg": None, "self_util": None, "limiting_joint": None})
                    continue
                for d in COM_OFFSETS:
                    m, u0, jl = max_mass(robot, q, gvecs, d, cap)
                    masses.append((d, m, jl))
                    rows.append({"model": model, "r_m": r, "z_m": z, "com_offset_m": d, "ik_err_m": round(err, 4),
                                 "max_mass_kg": round(m, 1), "self_util": round(u0, 3),
                                 "limiting_joint": f"A{jl + 1}" if jl >= 0 else ""})
        ok = [m for _, m, _ in masses]
        by_off = {str(d): round(min(m for dd, m, _ in masses if dd == d), 1) for d in COM_OFFSETS}
        lim = sorted({f"A{j + 1}" for _, m, j in masses if j >= 0 and m <= min(ok) * 1.05})
        summ["models"][model] = {
            "envelope_min_kg_by_com_offset_m": by_off,
            "limiting_joints_near_min": lim,
            "robot_mass_kg_from_urdf": round(robot.mass, 1),
            "effort_Nm": [round(t, 1) for t in robot.tau_max],
            "rated_payload_kg": RATED[model],
            "envelope_max_mass_min_kg": round(min(ok), 1) if ok else None,
            "envelope_max_mass_median_kg": round(float(np.median(ok)), 1) if ok else None,
            "usable_kg": round(min(RATED[model], min(ok)), 1) if ok else None,
            "poses_reached": len(ok) // len(COM_OFFSETS),
            "poses_total": len(RADII) * len(HEIGHTS),
        }
        p.removeBody(robot.uid, physicsClientId=cid)
    p.disconnect(cid)

    with open(out / "heavy_payload.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open(out / "summary_heavy_robot.json", "w", encoding="utf-8") as f:
        json.dump(summ, f, ensure_ascii=False, indent=2)

    print(f"토크 상한 {cap} x effort, 경사 {len(cases)}개 조건 중 최악, 자세 {len(RADII) * len(HEIGHTS)}개 x 질량중심 {len(COM_OFFSETS)}개")
    print("모델    로봇질량kg  정격kg  포락선 최소kg (질량중심 0.3 m / 0.6 m)  포락선 중앙kg  사용가능kg  제한 관절  도달자세")
    for k, s in summ["models"].items():
        bo = s["envelope_min_kg_by_com_offset_m"]
        print(f"{k:6s} {s['robot_mass_kg_from_urdf']:10.1f} {s['rated_payload_kg']:7.0f} {bo['0.3']:>14} / {bo['0.6']:<14} "
              f"{str(s['envelope_max_mass_median_kg']):>12s} {str(s['usable_kg']):>10s}  {','.join(s['limiting_joints_near_min']):8s} {s['poses_reached']}/{s['poses_total']}")
    print(f"\n출력 폴더: {out}")


if __name__ == "__main__":
    main()
