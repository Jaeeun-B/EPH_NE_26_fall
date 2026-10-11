"""Xe 포집 이중베드의 교체 주기, 부품 선량 예산, 필요 차폐, 모듈 질량을 한 번에 계산한다.

10/6 회의 결정(Xe 단일 타겟, 이중베드 유지)과 팀원 자료(정현: 파과시간, 서현: TID_lim = TID / RDM)를
E 파트 시뮬레이션과 잇는 계산이다.

흐름
  베드 운전시간 T_on ── 흡착제 질량 m (t = f·K·m/Q) ── 교체 횟수 N_ex = 수명 / T_on
        │                                              │
        └─ 교체 시점 Xe 재고 (MARINA 식) ─ 선원 세기 ─┐   └─ 부품 예산 B_k = TID_lim,k / N_ex
                                                     ▼
  B0 궤적의 부품별 단위 선량 d_k (선원 세기 1 Gy/h@1m 당) ─ 교체 1회 선량 D_k(x)
                                                     ▼
                       max_k D_k(x) / B_k <= 1 이 되는 차폐 두께 x ─ 모듈 질량 ─ 로봇 가반하중과 비교

선량은 MARINA 공개값과 가정으로 만든 상한 추정이다(ε = 1, 자체차폐·용기·빌드업 없음).
가상 선원 기준의 기존 결과(06, 07)는 바꾸지 않는다.

실행: python scripts/11_xe_bed_budget.py
출력: outputs/xe_bed/ unit_dose.csv, budget_table.csv, summary_xe_bed.json, xe_bed_budget.png
"""
import copy
import csv
import json
import math

import numpy as np

import _bootstrap  # noqa: F401
from datraj import OUTPUTS, config, viz_style
from datraj import xe_bed as X
from datraj.components import load as load_components
from datraj.dose_eval import ComponentDoseEvaluator, build_fields
from datraj.planning import make_rrt_planner
from datraj.scene import Scene
from datraj.task import build_trajectory, solve_chain

DAY = 86400.0
T_ON_DAYS = [0.25, 1, 3, 7, 14, 30]
T_C_DAYS = [0, 1, 3, 7, 14]
CONDITIONS = [  # (이름, 온도 °C, 압력 bar)
    ("25 °C, 1 bar", 25.0, 1.0),
    ("25 °C, 7 bar", 25.0, 7.0),
    ("0 °C, 7 bar", 0.0, 7.0),
]
MATERIALS = ["W", "Pb"]
SERVICE_YEARS = [1, 3, 9]  # C2: 흡착제 교체 간격 [년] (가정)


def unit_doses(scene, segs, comps):
    """선원별(bed_A, bed_B) 세기 1 Gy/h@1m 당 부품 누적선량 [Gy], 단계별 분해 포함."""
    base = config.virtual_sources()
    ev = ComponentDoseEvaluator(scene.robot, comps)
    out = {}
    for sid in ("bed_A", "bed_B"):
        vs = copy.deepcopy(base)
        for s in vs["sources"]:
            s["strength"] = 1.0 if s["id"] == sid else 0.0
        fields = build_fields("model", sources=vs)
        tot = np.zeros(len(comps))
        by_kind = {"plan": np.zeros(len(comps)), "line": np.zeros(len(comps)), "dwell": np.zeros(len(comps))}
        for seg in segs:
            d = ev.evaluate(seg.traj.t, seg.traj.q, fields[seg.step.field]).dose
            tot += d
            by_kind[seg.step.kind] += d
        out[sid] = {"total": tot, "by_kind": by_kind}
    return out


def main():
    cfg = X.load()
    out = OUTPUTS / "xe_bed"
    out.mkdir(parents=True, exist_ok=True)
    comps, _ = load_components()
    real = [k for k, c in enumerate(comps) if not c.reference]
    ids = [comps[k].id for k in real]
    bud = cfg["budget"]
    fail = np.array([bud["TID_fail_Gy"].get(i) if bud["TID_fail_Gy"].get(i) is not None else np.nan for i in ids], float)
    tid_lim = fail / bud["RDM"]
    life_s = bud["life_EFPY"] * 365.25 * DAY

    # 1) B0 궤적과 단위 선량
    task = config.task_config()
    scene = Scene()
    solved = solve_chain(scene, task)
    segs = build_trajectory(scene, solved, make_rrt_planner(task), task)
    U = unit_doses(scene, segs, comps)
    dA, dB = U["bed_A"]["total"][real], U["bed_B"]["total"][real]
    T_ex = sum(s.traj.duration for s in segs)
    with open(out / "unit_dose.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["component", "name", "d_bedA_Gy_per_GyPerHourAt1m", "d_bedB", "bedA_dwell_share", "TID_lim_Gy"])
        for j, k in enumerate(real):
            byk = U["bed_A"]["by_kind"]
            share = byk["dwell"][k] / U["bed_A"]["total"][k] if U["bed_A"]["total"][k] > 0 else float("nan")
            w.writerow([comps[k].id, comps[k].name, f"{dA[j]:.6e}", f"{dB[j]:.6e}", f"{share:.3f}",
                        "" if math.isnan(tid_lim[j]) else f"{tid_lim[j]:.2f}"])

    # 2) 시나리오 표
    #   C1 포집 후 교체: 파과 시점마다 교체. T_on = 파과시간, N_ex = 수명 / T_on, 운전 중 베드 B는 전환 후 t_c 동안 쌓인 재고
    #   C2 드문 교체: 재생(PSA 등) 또는 지연베드로 운전하고 흡착제 수명 끝에만 교체. 재고는 지연베드 정상상태(T_hold 90 d)
    #   B_fixed: 운전 중인 베드 B를 고정 차폐벽이 가린다고 보면 B 기여를 0으로 둔다
    robots = cfg["robots"]["candidates"]
    rows = []

    def add_row(concept, cname, TC, Pbar, Ton_d, tc_d, N_ex, m, A_A, A_B, b_fixed):
        lA, lB = X.strength_by_line(cfg, A_A), X.strength_by_line(cfg, A_B)
        sA, sB = sum(s for _, s in lA), (0.0 if b_fixed else sum(s for _, s in lB))
        D0 = sA * dA + sB * dB
        ratio0 = np.nanmax(D0 / (tid_lim / N_ex))
        # 로봇 부품을 1년마다 새것으로 바꾸면 부품 하나가 겪는 교체 횟수는 1년치로 줄어든다 (예비품 운용)
        N_ex_yearly = min(N_ex, 365.25 / Ton_d)

        def solve(mat, n_ex):
            budget = tid_lim / n_ex

            def worst(x):
                D = X.transmitted(cfg, lA, mat, x) * dA
                if not b_fixed:
                    D = D + X.transmitted(cfg, lB, mat, x) * dB
                return float(np.nanmax(D / budget))
            x = X.solve_thickness(worst, 1.0, x_max=0.30)
            mod = X.build_module(cfg, m, mat, x if x is not None else 0.30)
            ok = [r["id"] for r in robots
                  if x is not None and mod.mass <= min(r["rated_kg"], r["envelope_kg"] or r["rated_kg"])]
            return x, mod, ok

        for mat in MATERIALS:
            x, mod, ok = solve(mat, N_ex)
            xy, mody, oky = solve(mat, N_ex_yearly)
            rows.append({
                "concept": concept, "B_fixed_shield": b_fixed,
                "condition": cname, "T_on_d": Ton_d, "t_c_d": tc_d, "material": mat,
                "sorbent_kg": round(m, 2), "D_m": round(mod.D, 3), "H_m": round(mod.H, 3),
                "N_ex": round(N_ex, 1),
                "A_bedA_Bq": f"{sum(A_A.values()):.3e}", "S_bedA_GyPerH_1m": f"{sA:.3e}",
                "S_bedB_GyPerH_1m": f"{sB:.3e}",
                "worst_ratio_unshielded": f"{ratio0:.3e}",
                "x_req_mm": None if x is None else round(x * 1000, 1),
                "shield_kg": None if x is None else round(mod.m_shield, 1),
                "module_kg": None if x is None else round(mod.mass, 1),
                "outer_D_m": None if x is None else round(mod.D + 2 * (cfg["module"]["vessel_wall_m"] + x), 3),
                "robots_ok": " ".join(ok),
                "N_ex_per_robot_yearly_parts": round(N_ex_yearly, 1),
                "x_req_mm_yearly_parts": None if xy is None else round(xy * 1000, 1),
                "module_kg_yearly_parts": None if xy is None else round(mody.mass, 1),
                "robots_ok_yearly_parts": " ".join(oky),
            })

    for cname, TC, Pbar in CONDITIONS:
        for Ton_d in T_ON_DAYS:
            Ton = Ton_d * DAY
            m = X.sorbent_mass_kg(cfg, Ton, TC, Pbar)
            for tc_d in T_C_DAYS:
                if tc_d >= Ton_d:   # 베드 B가 파과되기 전에 냉각과 교체를 끝내야 한다
                    continue
                for b_fixed in (False, True):
                    add_row("C1 포집 후 교체", cname, TC, Pbar, Ton_d, tc_d, life_s / Ton, m,
                            X.bed_activity(cfg, Ton, tc_d * DAY), X.online_bed_activity(cfg, tc_d * DAY), b_fixed)
    T_hold = 90 * DAY
    for cname, TC, Pbar in CONDITIONS:
        m = X.sorbent_mass_kg(cfg, T_hold, TC, Pbar)
        for interval_y in SERVICE_YEARS:
            for tc_d in (7, 30, 90):
                add_row("C2 드문 교체", cname, TC, Pbar, interval_y * 365.25, tc_d, bud["life_EFPY"] / interval_y, m,
                        X.bed_activity(cfg, T_hold, tc_d * DAY), X.bed_activity(cfg, T_hold, 0.0), True)

    with open(out / "budget_table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # 3) 요약
    kA = int(np.nanargmax(dA))
    summ = {
        "note": "MARINA 공개값과 가정으로 만든 상한 추정. ε = 1, 베드 자체차폐·용기·빌드업 없음, 로봇은 교체 사이에 차폐된 대기 위치에 있다고 가정",
        "exchange_duration_s": round(T_ex, 2),
        "unit_dose_max_component": comps[real[kA]].id,
        "bedA_dwell_share_of_unit_dose_max_component": round(float(U["bed_A"]["by_kind"]["dwell"][real[kA]] / U["bed_A"]["total"][real[kA]]), 3),
        "K_cm3_per_g": {c: round(X.K_xe(cfg, TC), 1) for c, TC, _ in CONDITIONS},
        "sorbent_kg_per_day": {c: round(X.sorbent_mass_kg(cfg, DAY, TC, P), 2) for c, TC, P in CONDITIONS},
        "bedA_strength_T_on_7d_tc0_GyPerH_1m": round(X.strength_si(cfg, X.bed_activity(cfg, 7 * DAY, 0)), 1),
        "tid_lim_Gy": {i: (None if math.isnan(v) else round(v, 2)) for i, v in zip(ids, tid_lim)},
        "rows": len(rows),
    }
    with open(out / "summary_xe_bed.json", "w", encoding="utf-8") as f:
        json.dump(summ, f, ensure_ascii=False, indent=2)

    plot(rows, robots, out / "xe_bed_budget.png")
    print_summary(rows, summ)
    print(f"\n출력 폴더: {out}")


def print_summary(rows, summ):
    print(f"교체 1회 작업시간 {summ['exchange_duration_s']} s, 단위 선량 최대 부품 {summ['unit_dose_max_component']} "
          f"(Bed A 기여 중 체류 비중 {summ['bedA_dwell_share_of_unit_dose_max_component']:.0%})")
    print("흡착제 소요량 [kg/일]:", summ["sorbent_kg_per_day"])
    print(f"Bed A 선원 세기 (T_on 7 d, t_c 0): {summ['bedA_strength_T_on_7d_tc0_GyPerH_1m']} Gy/h @ 1 m (Si, 차폐 없음)")
    hdr = "개념            B고정  조건           T_on[d] t_c  흡착제kg  교체횟수  무차폐/예산  W두께mm  모듈kg  가능한 로봇"
    print("\n" + hdr)
    for r in rows:
        if r["material"] != "W":
            continue
        c1 = r["concept"].startswith("C1") and r["condition"] == "0 °C, 7 bar" and r["T_on_d"] in (0.25, 1, 7, 30)
        c2 = r["concept"].startswith("C2") and r["condition"] in ("25 °C, 1 bar", "0 °C, 7 bar")
        if c1 or c2:
            print(f"{r['concept']:12s} {str(r['B_fixed_shield']):6s} {r['condition']:13s} {r['T_on_d']:7g} {r['t_c_d']:4g} "
                  f"{r['sorbent_kg']:9.1f} {r['N_ex']:8.0f} {float(r['worst_ratio_unshielded']):11.2e} "
                  f"{str(r['x_req_mm']):>8s} {str(r['module_kg']):>8s}  {r['robots_ok']}")


def plot(rows, robots, path):
    import matplotlib.pyplot as plt
    viz_style.apply()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    W = [r for r in rows if r["concept"].startswith("C1") and r["material"] == "W"]

    def series(ax, sel, key, **kw):
        rr = sorted([r for r in W if sel(r) and r[key] is not None], key=lambda r: r["T_on_d"])
        if rr:
            ax.plot([r["T_on_d"] for r in rr], [r[key] for r in rr], marker="o", ms=3, **kw)

    ax = axes[0]
    for cname, _, _ in CONDITIONS:
        series(ax, lambda r, c=cname: r["condition"] == c and r["t_c_d"] == 0 and not r["B_fixed_shield"],
               "module_kg", label=cname)
    ax.set_title("현재 가정: 냉각 없음, 운전 베드 차폐 없음, 로봇 1대로 수명 전체")
    ax = axes[1]
    for tc, col in zip((0, 1, 3, 7), ("C0", "C1", "C2", "C3")):
        sel = lambda r, tc=tc: r["condition"] == "0 °C, 7 bar" and r["t_c_d"] == tc and r["B_fixed_shield"]  # noqa: E731
        series(ax, sel, "module_kg", color=col, label=f"t_c = {tc} 일")
        series(ax, sel, "module_kg_yearly_parts", color=col, ls="--", label=f"t_c = {tc} 일, 부품 매년 교체")
    ax.set_title("0 °C, 7 bar + 운전 베드 고정 차폐")
    for ax in axes:
        caps = {}
        for r in robots:
            cap = min(r["rated_kg"], r["envelope_kg"] or r["rated_kg"])
            key = int(cap // 20)   # 거의 같은 값(KR 210, KR 300)은 한 줄로 묶는다
            caps.setdefault(key, []).append((r["name"].replace("KUKA ", "").replace(" R2700-2", "").replace(" R820", ""), cap))
        groups = sorted((min(c for _, c in items), items) for items in caps.values())
        for gi, (cap, items) in enumerate(groups):
            ax.axhline(cap, color="0.55", lw=0.8, ls=":")
            crowded = gi + 1 < len(groups) and groups[gi + 1][0] / cap < 1.4
            ax.text(0.26, cap * (0.80 if crowded else 1.07), " / ".join(n for n, _ in items) + f" ({cap:g} kg)",
                    fontsize=7, color="0.35")
        ax.set_xscale("log")
        viz_style.log_axis(ax, "y")
        ax.set_xticks(T_ON_DAYS)
        ax.set_xticklabels([f"{t:g}" for t in T_ON_DAYS])
        ax.set_xlabel("베드 운전시간 T_on (= 교체 간격) [일]")
        ax.grid(True, which="both", alpha=0.3)
    axes[0].set_ylabel("교체 모듈 질량 (흡착제 + 용기 + W 차폐) [kg]")
    for ax in axes:
        ax.legend(fontsize=7, loc="upper left", frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
