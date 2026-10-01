"""검증 5-1 (1): 점선원 옆 직선 통과의 해석해 대조.

점선원 세기 S (1 m에서 Gy/h) 옆을 수직거리 d, 속도 v로 -L ~ L 직선 통과할 때
    D = S / (v d) * 2 atan(L / d) / 3600      [Gy]
(a) 시간 간격 dt에 따른 수치적분 오차 (해석 선량률 사용)
(b) 격자 해상도 N (25, 50, 100)에 따른 보간 오차 (방향·위치를 무작위로 바꿔 반복)

실행: python scripts/03_validate_line.py
출력: outputs/validation/line_dt.csv, line_grid.csv, line_validation.png
"""
import csv

import numpy as np

import _bootstrap  # noqa: F401
from datraj import OUTPUTS, config, viz_style
from datraj.dose_grid import DoseGrid
from datraj.dose_model import Source, dose_rate, grid_from_sources

S = 1.0          # Gy/h at 1 m
L = 0.5          # 반경로 길이 [m]
V = 0.1          # 속도 [m/s]
TRIALS = 24
OUT = OUTPUTS / "validation"


def analytic(d, v=V, s0=-L, s1=L, s=S):
    return s / (v * d) * (np.arctan(s1 / d) - np.arctan(s0 / d)) / 3600.0


def line_points(src, d, u, n_hat, ts, v=V, s0=-L):
    s = s0 + v * ts
    return src + d * n_hat + s[:, None] * u


def integrate(rates, ts):
    return np.trapezoid(rates, ts) / 3600.0


def random_frame(rng):
    u = rng.normal(size=3)
    u /= np.linalg.norm(u)
    n = np.cross(u, rng.normal(size=3))
    n /= np.linalg.norm(n)
    return u, n


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    layout = config.layout()
    lo = np.asarray(layout["cell"]["interior_min"], float)
    hi = np.asarray(layout["cell"]["interior_max"], float)
    rng = np.random.default_rng(7)
    T = 2 * L / V

    # (a) 시간 간격
    rows_dt = []
    src0 = np.array([0.2, 0.0, 1.0])
    point = [Source("p", "point", S, [src0], r_min=0.01)]
    u, n_hat = np.array([1.0, 0, 0]), np.array([0, 1.0, 0])
    for d in (0.1, 0.2, 0.3, 0.5):
        for dt in (5.0, 3.0, 2.0, 1.5, 1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01):
            # 최근접점이 샘플과 겹치지 않도록 경로를 dt의 0.37배만큼 민다
            s0 = -L + 0.37 * V * dt
            ts = np.arange(0, T + 1e-9, dt)
            D = integrate(dose_rate(line_points(src0, d, u, n_hat, ts, s0=s0), point), ts)
            ref = analytic(d, s0=s0, s1=s0 + V * ts[-1])
            err = abs(D - ref) / ref
            rows_dt.append({"d_m": d, "dt_s": dt, "step_m": V * dt, "step_over_d": V * dt / d,
                            "rel_err": err})
    with open(OUT / "line_dt.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows_dt[0].keys())
        w.writeheader()
        w.writerows(rows_dt)

    # (b) 격자 해상도
    rows_g = []
    ts = np.linspace(0, T, 2001)
    ds = (0.1, 0.15, 0.2, 0.3, 0.5)
    for N in (25, 50, 100):
        spacing = (hi - lo) / (N - 1)
        errs = {d: [] for d in ds}
        for k in range(TRIALS):
            # 선원을 격자 노드에서 무작위로 벗어난 위치에 둔다
            src = np.array([0.2, 0.0, 1.0]) + rng.uniform(-0.5, 0.5, 3) * spacing
            pt = [Source("p", "point", S, [src], r_min=0.01)]
            arr = grid_from_sources(pt, lo, spacing, (N, N, N))
            grid = DoseGrid(arr, {"origin": lo.tolist(), "spacing": spacing.tolist()})
            u, n_hat = random_frame(rng)
            for d in ds:
                D = integrate(grid(line_points(src, d, u, n_hat, ts), warn_outside=False), ts)
                errs[d].append((D - analytic(d)) / analytic(d))
        for d in ds:
            e = np.asarray(errs[d])
            rows_g.append({"N": N, "spacing_m": round(float(spacing[0]), 4), "d_m": d,
                           "mean_err": float(np.mean(e)), "max_abs_err": float(np.max(np.abs(e)))})
    with open(OUT / "line_grid.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows_g[0].keys())
        w.writeheader()
        w.writerows(rows_g)

    # 요약
    print("(a) 시간 간격: 상대오차 1% 이내가 되는 최대 경로 간격 (v*dt / d)")
    for d in (0.1, 0.2, 0.3, 0.5):
        ok = [r for r in rows_dt if r["d_m"] == d and r["rel_err"] < 0.01]
        best = max(ok, key=lambda r: r["dt_s"]) if ok else None
        print(f"  d={d:.2f} m: dt <= {best['dt_s']} s (경로 간격 {best['step_m']:.3f} m, d의 {best['step_over_d']:.2f}배)"
              if best else f"  d={d:.2f} m: 1% 미달")
    print("(b) 격자 보간: 최대 상대오차 (무작위 방향·위치 %d회, 양수 = 과대평가)" % TRIALS)
    for N in (25, 50, 100):
        line = ", ".join(f"d={r['d_m']:.2f}: {r['max_abs_err'] * 100:.1f}%"
                         for r in rows_g if r["N"] == N)
        sp = next(r["spacing_m"] for r in rows_g if r["N"] == N)
        print(f"  N={N:3d} (간격 {sp:.3f} m): {line}")

    # 그림
    viz_style.apply()
    import matplotlib.pyplot as plt

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
    for i, d in enumerate((0.1, 0.2, 0.3, 0.5)):
        rr = [r for r in rows_dt if r["d_m"] == d]
        a1.plot([r["step_over_d"] for r in rr], [r["rel_err"] * 100 for r in rr], "-o", ms=4,
                color=viz_style.CATEGORICAL[i], label=f"d = {d} m")
    a1.axhline(1.0, color=viz_style.MUTED, lw=1, ls="--")
    a1.text(a1.get_xlim()[0] if False else 0.012, 1.15, "1%", color=viz_style.MUTED, fontsize=8)
    a1.set_xscale("log")
    a1.set_yscale("log")
    a1.set_xlabel("경로 간격 / 수직거리  (v·dt / d)")
    a1.set_ylabel("상대오차 [%]")
    a1.set_title("(a) 시간 간격에 따른 적분 오차", loc="left")
    a1.legend()
    a1.grid(True, which="major")
    for i, N in enumerate((25, 50, 100)):
        rr = [r for r in rows_g if r["N"] == N]
        a2.plot([r["d_m"] for r in rr], [r["max_abs_err"] * 100 for r in rr], "-o", ms=4,
                color=viz_style.CATEGORICAL[i], label=f"N = {N} (간격 {rr[0]['spacing_m'] * 100:.1f} cm)")
    a2.axhline(1.0, color=viz_style.MUTED, lw=1, ls="--")
    a2.set_yscale("log")
    a2.set_xlabel("선원까지 수직거리 d [m]")
    a2.set_ylabel("최대 상대오차 [%]")
    a2.set_title("(b) 격자 해상도에 따른 보간 오차", loc="left")
    a2.legend()
    a2.grid(True, which="major")
    fig.savefig(OUT / "line_validation.png")
    print(f"그림: {OUT / 'line_validation.png'}")


if __name__ == "__main__":
    main()
