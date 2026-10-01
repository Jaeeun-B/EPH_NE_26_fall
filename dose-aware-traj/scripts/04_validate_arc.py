"""검증 5-1 (2): 참고문헌 3 조건 재현 (선원에서 1 m 떨어진 원호를 20 mm/s로 60 s 이동).

배치: 점선원을 로봇 A1 축 위 높이 z_s에 두고, TCP가 수평 반경 0.6 m, 높이 z_s - 0.8 m의 원호를 돈다.
TCP와 선원 사이 거리는 항상 sqrt(0.6^2 + 0.8^2) = 1.0 m. 원호 길이 1.2 m = 20 mm/s x 60 s.
A1만 회전하므로 모든 부품의 선원 거리가 일정하다 -> 부품마다 해석해 D_k = S / r_k^2 x 60 s 가 있다.

확인하는 것
1. TCP 선량이 Ḋ(1 m) x 60 s 와 일치하는지 (순기구학 + 적분 파이프라인 점검)
2. 같은 궤적에서 부품별 선량 분포 (점 로봇 가정과의 차이)
3. 격자 보간(N=50, 100)을 거쳤을 때의 오차

실행: python scripts/04_validate_arc.py
출력: outputs/validation/arc_ref3.csv, arc_ref3.png
"""
import csv

import numpy as np
import pybullet as p

import _bootstrap  # noqa: F401
from datraj import OUTPUTS, config, viz_style
from datraj.components import load as load_components
from datraj.dose_eval import ComponentDoseEvaluator, GridField, SourceField
from datraj.dose_grid import DoseGrid
from datraj.dose_model import Source, grid_from_sources
from datraj.geometry import tool_down_R
from datraj.robot import Robot

S = 1.0           # Gy/h at 1 m
RHO = 0.6         # TCP 수평 반경 [m]
DZ = 0.8          # 선원과 TCP의 높이 차 [m]
Z_SRC = 1.05      # 선원 높이 [m]
SPEED = 0.02      # m/s
DURATION = 60.0   # s
OUT = OUTPUTS / "validation"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    params = config.shared_params()
    layout = config.layout()
    cid = p.connect(p.DIRECT)
    robot = Robot(cid, params)
    comps, _ = load_components()
    ev = ComponentDoseEvaluator(robot, comps)

    src_pos = np.array([0.0, 0.0, Z_SRC])
    src = [Source("ref3", "point", S, [src_pos], r_min=0.01)]
    omega = SPEED / RHO
    phi0 = -omega * DURATION / 2
    tcp0 = np.array([RHO * np.cos(phi0), RHO * np.sin(phi0), Z_SRC - DZ])
    q0 = robot.ik_tcp(tcp0, tool_down_R(phi0 + np.pi), rest=np.array([0, 0.6, 0, -1.2, 0, 1.3, 0]))
    if q0 is None:
        raise SystemExit("시작 자세 IK 실패")
    ts = np.linspace(0, DURATION, 601)
    qs = np.repeat(q0[None, :], len(ts), axis=0)
    qs[:, 0] = q0[0] + omega * ts
    if np.any(qs[:, 0] > robot.upper[0]) or np.any(qs[:, 0] < robot.lower[0]):
        raise SystemExit("A1 범위 초과")

    P, tcp, _ = ev.positions(qs)
    r_tcp = np.linalg.norm(tcp - src_pos, axis=1)
    arc_len = np.sum(np.linalg.norm(np.diff(tcp, axis=0), axis=1))
    r_k = np.linalg.norm(P - src_pos, axis=2)          # (T, K)
    D_exact = S / r_k.mean(axis=0) ** 2 * DURATION / 3600.0

    res_model = ev.evaluate(ts, qs, SourceField(src))
    lo = np.asarray(layout["cell"]["interior_min"], float)
    hi = np.asarray(layout["cell"]["interior_max"], float)
    res_grid = {}
    for N in (50, 100):
        spacing = (hi - lo) / (N - 1)
        arr = grid_from_sources(src, lo, spacing, (N, N, N))
        res_grid[N] = ev.evaluate(ts, qs, GridField(DoseGrid(arr, {"origin": lo.tolist(), "spacing": spacing.tolist(),
                                                                   "grid_id": f"ref3_N{N}"})))

    tcp_k = next(i for i, c in enumerate(comps) if c.id == "P0")
    D_tcp_ref = S / 1.0 ** 2 * DURATION / 3600.0
    print(f"TCP-선원 거리: {r_tcp.min():.5f} ~ {r_tcp.max():.5f} m, 원호 길이 {arc_len:.4f} m, 시간 {DURATION:.0f} s")
    print(f"TCP 선량: 계산 {res_model.dose[tcp_k] * 1e3:.5f} mGy / 기준 Ḋ(1 m) x 60 s = {D_tcp_ref * 1e3:.5f} mGy "
          f"(오차 {abs(res_model.dose[tcp_k] / D_tcp_ref - 1) * 100:.3f}%)")
    rows = []
    print(f"{'ID':4s} {'부품':16s} {'거리[m]':>8s} {'해석해[mGy]':>11s} {'파이프라인':>10s} {'격자50 오차':>10s} {'격자100 오차':>11s} {'TCP 대비':>8s}")
    for k, c in enumerate(comps):
        e50 = res_grid[50].dose[k] / D_exact[k] - 1
        e100 = res_grid[100].dose[k] / D_exact[k] - 1
        rows.append({"id": c.id, "name": c.name, "distance_m": r_k[:, k].mean(), "D_analytic_Gy": D_exact[k],
                     "D_pipeline_Gy": res_model.dose[k], "err_pipeline": res_model.dose[k] / D_exact[k] - 1,
                     "err_grid50": e50, "err_grid100": e100, "ratio_to_tcp": res_model.dose[k] / res_model.dose[tcp_k]})
        print(f"{c.id:4s} {c.name:16s} {r_k[:, k].mean():8.3f} {D_exact[k] * 1e3:11.4f} {res_model.dose[k] * 1e3:10.4f} "
              f"{e50 * 100:9.2f}% {e100 * 100:10.2f}% {rows[-1]['ratio_to_tcp']:8.2f}")
    with open(OUT / "arc_ref3.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    viz_style.apply()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    short = {"C08": "공구", "C09": "카메라", "C10": "베이스", "P0": "TCP"}
    labels = [f"{r['id']}\n{short.get(r['id'], r['name'].replace(' 구동부', ''))}" for r in rows]
    vals = [r["D_pipeline_Gy"] * 1e3 for r in rows]
    colors = [viz_style.MUTED if c.reference else viz_style.CATEGORICAL[0] for c in comps]
    ax.bar(range(len(rows)), vals, color=colors, width=0.62)
    ax.axhline(D_tcp_ref * 1e3, color=viz_style.INK_2, lw=1, ls="--", label="점 로봇(TCP) 값 = Ḋ(1 m) × 60 s")
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.set_xticks(range(len(rows)), labels, fontsize=7.5)
    ax.set_ylabel("60 s 누적선량 [mGy]")
    ax.set_title("참고문헌 3 조건: TCP가 선원에서 1 m 떨어진 원호를 20 mm/s로 이동할 때 부품별 선량", loc="left")
    ax.grid(True, axis="y")
    ax.set_axisbelow(True)
    fig.savefig(OUT / "arc_ref3.png")
    print(f"그림: {OUT / 'arc_ref3.png'}")


if __name__ == "__main__":
    main()
