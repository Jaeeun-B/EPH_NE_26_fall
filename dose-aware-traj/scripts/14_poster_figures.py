"""포스터(E 파트 패널)용 수치와 그림.

전제: 06, 07, 11, 13을 먼저 실행 (outputs/b0, b1, p3, xe_bed)
하는 일
1) B0, B1, P3 궤적 CSV에서 부품별 선량을 구간 종류(체류, 근접 직선, 경로계획)별로 다시 적분
   (dose_by_component_*.csv 합계와 일치하는지 확인)
2) 민감도: 손목 카메라(C09) 장착 위치를 공구 축 방향으로 뒤로 옮길 때 C09 선량 (B0 궤적 고정)
3) 포스터 그림 3장 (PNG 300 dpi + PDF)
   fig1_component_dose: 부품별 누적선량 (C09 = 1 상대값), 구간 종류별 누적 막대 + TCP
   fig2_levers: B0 대비 변화율 (경로 B1, 자세 P3, 카메라 위치)
   fig3_exchange: Xe 베드 교체 모듈 질량 대 교체 간격, 로봇 허용 하중

실행: python scripts/14_poster_figures.py
출력: outputs/poster/
"""
import csv
import json
from dataclasses import replace

import numpy as np

import _bootstrap  # noqa: F401
from datraj import OUTPUTS, ROOT, viz_style
from datraj.components import load as load_components
from datraj.dose_eval import ComponentDoseEvaluator, build_fields
from datraj.scene import Scene
from datraj.task import apply_state, task_steps

OUT = OUTPUTS / "poster"
KINDS = [("dwell", "체류 (해제·체결·파지)"), ("line", "베드 근처 직선 (5 cm/s)"), ("plan", "경로계획 구간")]
CAM_SHIFTS = [0.0, 0.10, 0.20]   # C09를 공구 축 방향으로 뒤로 옮기는 거리 [m]


def load_traj(tag):
    with open(OUTPUTS / tag / f"traj_{tag}.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    t = np.array([float(r["t"]) for r in rows])
    seg = np.array([int(r["segment"]) for r in rows])
    q = np.array([[float(r[f"q_A{j}"]) for j in range(1, 8)] for r in rows])
    return t, seg, q


def per_segment_dose(scene, comps, fields, tag):
    """(구간 수, 부품 수) Gy. 각 구간은 직전 구간의 마지막 시점부터 적분한다 (CSV는 경계 중복을 뺀 형태)."""
    steps = task_steps()
    t, seg, q = load_traj(tag)
    ev = ComponentDoseEvaluator(scene.robot, comps)
    out = np.zeros((seg.max() + 1, len(comps)))
    for s in range(seg.max() + 1):
        idx = np.nonzero(seg == s)[0]
        if s > 0:
            idx = np.concatenate([[idx[0] - 1], idx])
        st = steps[s]
        apply_state(scene, st.state)
        P, tcp, R = ev.positions(q[idx])
        r = fields[st.field].rate(P, tcp, R, t[idx]) * ev.S[None, :]
        out[s] = np.trapezoid(r, t[idx], axis=0) / 3600.0
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    scene = Scene()
    comps, _ = load_components()
    fields = build_fields("model")
    steps = task_steps()
    ids = [c.id for c in comps]
    real = [k for k, c in enumerate(comps) if not c.reference]
    k09, kT = ids.index("C09"), ids.index("P0")

    # 1) 구간 종류별 부품 선량
    seg_dose, by_kind = {}, {}
    for tag in ("b0", "b1", "p3"):
        sd = per_segment_dose(scene, comps, fields, tag)
        with open(OUTPUTS / tag / f"dose_by_component_{tag}.csv", encoding="utf-8") as f:
            ref = np.array([float(r["D_total_Gy"]) for r in csv.DictReader(f)])
        err = np.max(np.abs(sd.sum(0) / ref - 1))
        print(f"{tag}: 재적분 합계 vs CSV 최대 차이 {err * 100:.4f}%")
        assert err < 1e-3, "재적분 결과가 CSV와 다름"
        seg_dose[tag] = sd
        by_kind[tag] = {k: sd[[i for i, st in enumerate(steps) if st.kind == k]].sum(0) for k, _ in KINDS}

    # 2) 카메라 장착 위치 민감도 (B0 궤적 고정)
    cam = []
    base = comps[k09]
    for dz in CAM_SHIFTS:
        c2 = list(comps)
        c2[k09] = replace(base, offset=np.asarray(base.offset, float) - np.array([0, 0, dz]))
        d = per_segment_dose(scene, c2, fields, "b0").sum(0)[k09]
        cam.append({"shift_m": dz, "offset_link7_m": [float(v) for v in c2[k09].offset], "C09_Gy": float(d)})
    for c in cam:
        c["change_pct"] = (c["C09_Gy"] / cam[0]["C09_Gy"] - 1) * 100
    print("카메라 위치 민감도:", [(c["shift_m"], round(c["change_pct"], 1)) for c in cam])

    # 수치 정리
    tot = {tag: sd.sum(0) for tag, sd in seg_dose.items()}

    def pct(a, b):
        return float((a / b - 1) * 100)

    xe = json.load(open(OUTPUTS / "xe_bed" / "summary_xe_bed.json", encoding="utf-8"))
    p3 = json.load(open(OUTPUTS / "p3" / "summary_p3.json", encoding="utf-8"))
    from datraj import xe_bed as X
    from datraj.posture import budget_weights
    w = budget_weights(comps, X.load())
    nums = {
        "relative_to_C09_b0": {ids[k]: float(tot["b0"][k] / tot["b0"][k09]) for k in range(len(comps))},
        "kind_share_b0_pct": {k: float(by_kind["b0"][k][real].sum() / tot["b0"][real].sum() * 100) for k, _ in KINDS},
        "C09_dwell_share_b0_pct": float(by_kind["b0"]["dwell"][k09] / tot["b0"][k09] * 100),
        "levers_pct_vs_b0": {
            "B1_path": {"sum": pct(tot["b1"][real].sum(), tot["b0"][real].sum()),
                        "J": pct(w @ tot["b1"], w @ tot["b0"]),
                        "C09": pct(tot["b1"][k09], tot["b0"][k09]), "TCP": pct(tot["b1"][kT], tot["b0"][kT])},
            "P3_posture": {"sum": pct(tot["p3"][real].sum(), tot["b0"][real].sum()),
                           "J": pct(w @ tot["p3"], w @ tot["b0"]),
                           "C09": pct(tot["p3"][k09], tot["b0"][k09]), "TCP": pct(tot["p3"][kT], tot["b0"][kT]),
                           "best_component": min(((ids[k], pct(tot["p3"][k], tot["b0"][k])) for k in real),
                                                 key=lambda x: x[1])},
            "camera_shift": cam,
        },
        "p3_time_s": p3["T_total_s"], "p3_torque": p3["max_torque_utilization_envelope"],
        "xe": {k: xe[k] for k in ("sorbent_kg_per_day", "bedA_strength_T_on_7d_tc0_GyPerH_1m", "tid_lim_Gy")},
    }
    with open(OUT / "poster_numbers.json", "w", encoding="utf-8") as f:
        json.dump(nums, f, ensure_ascii=False, indent=2)

    figures(comps, tot, by_kind, real, k09, kT, nums)
    print(json.dumps(nums["levers_pct_vs_b0"], ensure_ascii=False, indent=1))
    print(f"출력 폴더: {OUT}")


def _style(scale=1.0):
    import matplotlib.pyplot as plt
    viz_style.apply()
    plt.rcParams.update({"font.size": 11 * scale, "axes.titlesize": 12 * scale, "axes.labelsize": 11 * scale,
                         "xtick.labelsize": 10 * scale, "ytick.labelsize": 10 * scale,
                         "legend.fontsize": 10 * scale, "axes.spines.top": False, "axes.spines.right": False})
    return plt


def _save(fig, name):
    # 포스터는 흰 바탕에 인쇄하므로 그림 배경도 흰색
    for ax in fig.axes:
        ax.set_facecolor("white")
    for ext, kw in (("png", {"dpi": 300}), ("pdf", {}), ("svg", {})):
        fig.savefig(OUT / f"{name}.{ext}", facecolor="white", **kw)


def figures(comps, tot, by_kind, real, k09, kT, nums):
    plt = _style()
    C = viz_style.CATEGORICAL
    ids = [c.id for c in comps]

    # fig1: 부품별 누적선량 (B0, C09 = 1), 구간 종류별 누적 + TCP
    order = sorted(real, key=lambda k: tot["b0"][k])
    labels = [f"{comps[k].id} {comps[k].name}" for k in order] + ["TCP (점 로봇 가정)"]
    ref = tot["b0"][k09]
    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    y = np.arange(len(labels))
    left = np.zeros(len(labels))
    for (kind, name), col in zip(KINDS, C[:3]):
        vals = np.array([by_kind["b0"][kind][k] for k in order] + [by_kind["b0"][kind][kT]]) / ref
        ax.barh(y, vals, left=left, color=col, height=0.68, label=name, edgecolor=viz_style.SURFACE, linewidth=1.0)
        left += vals
    ax.barh(y[-1], left[-1], height=0.68, fill=False, edgecolor=viz_style.INK_2, linewidth=1.0, hatch="///")
    for yi, v in zip(y, left):
        ax.text(v + 0.02, yi, f"{v:.2f}", va="center", fontsize=9, color=viz_style.INK_2)
    ax.axvline(1.0, color=viz_style.MUTED, lw=0.8, ls=":")
    ax.set_yticks(y, labels)
    ax.set_xlabel("작업 전체 누적선량 (손목 카메라 C09 = 1, 가상 선원)")
    ax.set_xlim(0, left.max() * 1.15)
    ax.grid(axis="x", color=viz_style.GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    _save(fig, "fig1_component_dose")
    plt.close(fig)

    # fig2: B0 대비 변화율 (같은 TCP라도 부품 선량은 달라진다)
    L = nums["levers_pct_vs_b0"]
    cam20 = next(c for c in L["camera_shift"] if abs(c["shift_m"] - 0.20) < 1e-9)
    groups = [f"경로 최적화 (B1)\n가중합 J {L['B1_path']['J']:+.1f}%",
              f"체류 자세 최적화 (P3)\n가중합 J {L['P3_posture']['J']:+.1f}%",
              "카메라 장착 위치\n20 cm 뒤로 (민감도)"]
    series = [("손목 카메라 C09", [L["B1_path"]["C09"], L["P3_posture"]["C09"], cam20["change_pct"]]),
              ("TCP (점 로봇 가정)", [L["B1_path"]["TCP"], L["P3_posture"]["TCP"], 0.0])]
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    h = 0.34
    yg = np.arange(len(groups))
    for si, ((name, vals), col) in enumerate(zip(series, (C[0], C[1]))):
        for gi, v in enumerate(vals):
            yy = yg[gi] + (si - 0.5) * h
            ax.barh(yy, v, height=h * 0.86, color=col, label=name if gi == 0 else None,
                    edgecolor=viz_style.SURFACE, linewidth=0.8)
            txt = f"{v:+.1f}%" if abs(v) >= 0.05 else "0.0%"
            if v < -8:
                ax.text(v - 1.0, yy, txt, va="center", ha="right", fontsize=9, color=viz_style.INK_2)
            else:
                ax.text(min(v, 0) - 1.0, yy, txt, va="center", ha="right", fontsize=9, color=viz_style.INK_2)
    ax.axvline(0, color=viz_style.INK_2, lw=0.8)
    ax.set_yticks(yg, groups)
    ax.invert_yaxis()
    ax.set_xlabel("B0(시간 최소 기준선) 대비 작업 전체 선량 변화 [%]")
    ax.set_xlim(-80, 4)
    ax.grid(axis="x", color=viz_style.GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 1.0), frameon=False, fontsize=9.5)
    fig.tight_layout()
    _save(fig, "fig2_levers")
    plt.close(fig)

    # fig3: Xe 베드 교체 모듈 질량 대 교체 간격
    with open(OUTPUTS / "xe_bed" / "budget_table.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    xe_cfg = json.load(open(ROOT / "config" / "xe_bed.json", encoding="utf-8"))

    def series_of(cond, tc, fixed, key):
        rr = [r for r in rows if r["concept"].startswith("C1") and r["material"] == "W" and r["condition"] == cond
              and float(r["t_c_d"]) == tc and r["B_fixed_shield"] == fixed and r[key]]
        rr.sort(key=lambda r: float(r["T_on_d"]))
        return [float(r["T_on_d"]) for r in rr], [float(r[key]) for r in rr]

    fig, ax = plt.subplots(figsize=(6.2, 3.9))
    x0, y0 = series_of("25 °C, 1 bar", 0, "False", "module_kg")
    x1, y1 = series_of("0 °C, 7 bar", 3, "True", "module_kg_yearly_parts")
    ax.plot(x0, y0, color=C[1], lw=2, marker="o", ms=4, label="현재 가정 (상온·대기압, 냉각·차폐벽 없음)")
    ax.plot(x1, y1, color=C[0], lw=2, marker="o", ms=4,
            label="0 °C·7 bar + 운전 베드 차폐벽\n+ 3일 냉각 + 로봇 부품 매년 교체")
    caps = {}
    for r in xe_cfg["robots"]["candidates"]:
        cap = min(r["rated_kg"], r["envelope_kg"] or r["rated_kg"])
        caps.setdefault(int(cap // 20), []).append((r["name"].replace("KUKA ", "").replace(" R2700-2", "")
                                                   .replace(" R820", "").replace("LBR ", ""), cap))
    groups_ = sorted((min(c for _, c in items), items) for items in caps.values())
    for gi, (cap, items) in enumerate(groups_):
        ax.axhline(cap, color=viz_style.MUTED, lw=0.8, ls="--")
        crowded = gi + 1 < len(groups_) and groups_[gi + 1][0] / cap < 1.4
        ax.text(0.22, cap * (0.95 if crowded else 1.05), " / ".join(n for n, _ in items) + f" 허용 {cap:g} kg",
                va="top" if crowded else "bottom", ha="left", fontsize=8.5, color=viz_style.INK_2)
    ax.annotate("로봇 직접 교체 가능\n(모듈 약 120 kg)", xy=(x1[0], y1[0]), xytext=(2.2, 45),
                fontsize=8.5, color=viz_style.INK, ha="center",
                arrowprops=dict(arrowstyle="-", color=viz_style.INK_2, lw=0.8))
    ax.set_xscale("log")
    viz_style.log_axis(ax, "y")
    ticks = [0.25, 1, 3, 7, 14, 30]
    ax.set_xticks(ticks, [f"{t:g}" for t in ticks])
    ax.set_xlim(0.2, 30)
    ax.set_xlabel("베드 운전시간 = 교체 간격 [일]")
    ax.set_ylabel("교체 모듈 질량 [kg]\n(흡착제 + 용기 + W 차폐)")
    ax.grid(True, which="major", color=viz_style.GRID, lw=0.6)
    ax.set_ylim(8, 3e4)
    ax.legend(loc="upper left", frameon=False, fontsize=8.5)
    fig.tight_layout()
    _save(fig, "fig3_exchange")
    plt.close(fig)


if __name__ == "__main__":
    main()
