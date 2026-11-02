"""포스터(E 파트 패널)용 수치와 그림.

전제: 06, 07, 11, 13, 15, 16을 먼저 실행 (outputs/b0, b1, p3, xe_bed, camera, design)
하는 일
1) B0, B1, P3 궤적 CSV에서 부품별 선량을 구간 종류(체류, 근접 직선, 경로계획)별로 다시 적분
   (dose_by_component_*.csv 합계와 일치하는지 확인)
2) 카메라 장착 위치: 15에서 찾은 장착 가능 위치로 C09를 옮겨 같은 방식으로 다시 적분
3) 포스터 그림 3장 (PNG 300 dpi + PDF + SVG)과 장면 그림
   fig1_component_dose: 부품별 누적선량 (C09 = 1 상대값), 구간 종류별 누적 막대 + TCP
   fig2_levers: B0 대비 변화율 (경로 B1, 자세 P3, 카메라 장착 위치, P3 + 카메라)
   fig3_exchange: 설계 방식별 교체 모듈 질량 대 교체 간격 (16), 로봇 허용 하중
   scene_dwell: S2 체류 자세(P3)와 카메라 현재 위치·변경 위치

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
KINDS = [("dwell", "Dwell (unlock, lock, grasp)"), ("line", "Near-bed moves (5 cm/s)"),
         ("plan", "Planned transfers")]


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

    # 2) 카메라 장착 위치 (15의 궤적별 전체 최적 위치로 C09만 옮김)
    place = json.load(open(OUTPUTS / "camera" / "placement.json", encoding="utf-8"))
    tot = {tag: sd.sum(0) for tag, sd in seg_dose.items()}
    for tag in ("b0", "p3"):
        b = place[tag]["best"]
        c2 = list(comps)
        c2[k09] = replace(comps[k09], link=int(b["link"]), offset=np.asarray(b["offset"], float))
        sd = per_segment_dose(scene, c2, fields, tag)
        assert abs(sd.sum(0)[k09] / b["C09_Gy"] - 1) < 1e-6, "15와 C09 선량이 다름"
        tot[f"{tag}_cam"] = sd.sum(0)

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
            "camera_placement": {"J": pct(w @ tot["b0_cam"], w @ tot["b0"]),
                                 "C09": pct(tot["b0_cam"][k09], tot["b0"][k09]), "TCP": 0.0,
                                 "mount": place["b0"]["best"],
                                 "C09_range_constraints": [min(x["C09_change_pct"] for x in place["sensitivity_b0"]),
                                                           max(x["C09_change_pct"] for x in place["sensitivity_b0"])],
                                 "A7_tool_only": place["b0"]["best_by_link"].get("A7 링크·공구", {}).get("change_pct")},
            "P3_plus_camera": {"sum": pct(tot["p3_cam"][real].sum(), tot["b0"][real].sum()),
                               "J": pct(w @ tot["p3_cam"], w @ tot["b0"]),
                               "C09": pct(tot["p3_cam"][k09], tot["b0"][k09]), "TCP": pct(tot["p3"][kT], tot["b0"][kT]),
                               "mount": place["p3"]["best"]},
            "camera_unconstrained_shift": place["b0"]["shift_check"],
        },
        "relative_to_C09_b0_cam": {ids[k]: float(tot["b0_cam"][k] / tot["b0_cam"][real].max()) for k in real},
        "p3_time_s": p3["T_total_s"], "p3_torque": p3["max_torque_utilization_envelope"],
        "xe": {k: xe[k] for k in ("sorbent_kg_per_day", "bedA_strength_T_on_7d_tc0_GyPerH_1m", "tid_lim_Gy")},
        "design": design_numbers(),
    }
    with open(OUT / "poster_numbers.json", "w", encoding="utf-8") as f:
        json.dump(nums, f, ensure_ascii=False, indent=2)

    f1, f2, f3, f3s = fig_data(comps, tot, by_kind, real, k09, kT, nums)
    figures(f1, f2, f3, f3s)
    export_tables(f1, f2, f3, f3s)
    scene_figure(scene, comps, k09, place["p3"]["best"])
    print(json.dumps(nums["levers_pct_vs_b0"], ensure_ascii=False, indent=1))
    print(json.dumps(nums["design"], ensure_ascii=False, indent=1))
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


EN_NAME = {"C01": "A1 drive", "C02": "A2 drive", "C03": "A3 drive", "C04": "A4 drive", "C05": "A5 drive",
           "C06": "A6 drive", "C07": "A7 drive", "C08": "Tool drive", "C09": "Wrist camera",
           "C10": "Base connector", "P0": "TCP (point-robot model)"}
FIG_W = 4.9   # 포스터 패널의 한 단 너비(약 125 mm)와 같게 두어 글자 크기가 그대로 인쇄되게 한다 [in]
DESIGNS = [("tcp", "Point-robot (TCP) design"), ("b0", "Component-level design (B0 = P3)"),
           ("p3_cam", "Component-level + camera mount (P3)")]


def design_numbers():
    """16 결과 중 포스터에 쓰는 값."""
    d = json.load(open(OUTPUTS / "design" / "summary_design.json", encoding="utf-8"))
    out = {"key_scenario": d["key_scenario"], "check_vs_11": d["check_vs_11_max_rel_err"], "designs": {}}
    for key, dd in d["designs"].items():
        k7 = next(r for r in dd["key_rows"] if r["T_on_d"] == 7)
        rng = dd["T_on_range_by_robot_yearly_parts"]
        out["designs"][key] = {
            "name": dd["name"],
            "worst_ratio_rel_b0": dd["worst_ratio_rel_b0"],
            "limiting": [(x["id"], x["rel_to_b0_C09"]) for x in dd["limiting_bedA"]],
            "T_on_7d_W_mm": k7["x_req_mm_yearly_parts"], "T_on_7d_module_kg": k7["module_kg_yearly_parts"],
            "T_on_max_kr120_d": rng["kr120"][1] if rng["kr120"] else None,
            "T_on_max_kr210_d": rng["kr210"][1] if rng["kr210"] else None,
            "C1_W_robot_ok_yearly_parts": dd["C1_W_robot_ok_yearly_parts"],
        }
    return out


def robot_caps():
    xe_cfg = json.load(open(ROOT / "config" / "xe_bed.json", encoding="utf-8"))
    caps = {}
    for r in xe_cfg["robots"]["candidates"]:
        cap = min(r["rated_kg"], r["envelope_kg"] or r["rated_kg"])
        caps.setdefault(int(cap // 20), []).append((r["name"].replace("KUKA ", "").replace(" R2700-2", "")
                                                   .replace(" R820", "").replace("LBR ", ""), cap))
    return sorted((min(c for _, c in items), items) for items in caps.values())


def fig_data(comps, tot, by_kind, real, k09, kT, nums):
    """그림 3장의 데이터 표 (그림과 Numbers용 내보내기가 같은 표를 쓴다)."""
    order = sorted(real, key=lambda k: tot["b0"][k])
    ref = tot["b0"][k09]
    f1 = [{"Component": f"{comps[k].id} {EN_NAME[comps[k].id]}",
           **{name: float(by_kind["b0"][kind][k] / ref) for kind, name in KINDS}} for k in order]
    f1.append({"Component": EN_NAME["P0"], **{name: float(by_kind["b0"][kind][kT] / ref) for kind, name in KINDS}})
    L = nums["levers_pct_vs_b0"]
    f2 = [{"Lever": "Path optimization (B1)", "key": "B1_path"},
          {"Lever": "Dwell posture optimization (P3)", "key": "P3_posture"},
          {"Lever": "Camera mount optimization", "key": "camera_placement"},
          {"Lever": "P3 + camera mount", "key": "P3_plus_camera"}]
    for r in f2:
        v = L[r["key"]]
        r.update({"Wrist camera C09 [%]": v["C09"], "TCP (point-robot model) [%]": v["TCP"],
                  "Weighted sum J [%]": v["J"]})
        lo, hi = (v["C09_range_constraints"] if r["key"] == "camera_placement" else (None, None))
        r.update({"C09 range low [%]": lo, "C09 range high [%]": hi})
    with open(OUTPUTS / "design" / "design_fine.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    T = sorted({float(r["T_on_d"]) for r in rows})
    f3 = []
    for t in T:
        rec = {"Exchange interval [days]": t}
        for key, name in DESIGNS:
            r = next(r for r in rows if r["design"] == key and float(r["T_on_d"]) == t)
            rec[name + " [kg]"] = float(r["module_kg_yearly_parts"]) if r["module_kg_yearly_parts"] else None
        for cap, items in robot_caps():
            if cap > 30:
                rec[" / ".join(n for n, _ in items) + " limit [kg]"] = cap
        f3.append(rec)
    D = nums["design"]["designs"]
    f3s = [{"Design": name, "Max interval with KR 120 [days]": D[key]["T_on_max_kr120_d"],
            "Max interval with KR 210 [days]": D[key]["T_on_max_kr210_d"],
            "Module mass at 7-day interval [kg]": D[key]["T_on_7d_module_kg"],
            "W shield at 7-day interval [mm]": D[key]["T_on_7d_W_mm"],
            "Limiting part": f"{D[key]['limiting'][0][0]} {EN_NAME[D[key]['limiting'][0][0]]}",
            "Exchanges per year with KR 120": (365.25 / D[key]["T_on_max_kr120_d"]
                                               if D[key]["T_on_max_kr120_d"] else None)} for key, name in DESIGNS]
    return f1, f2, f3, f3s


def figures(f1, f2, f3, f3s):
    plt = _style()
    C = viz_style.CATEGORICAL

    # fig1: 부품별 누적선량 (B0, C09 = 1), 구간 종류별 누적 + TCP
    labels = [r["Component"] for r in f1]
    fig, ax = plt.subplots(figsize=(FIG_W, 3.9))
    y = np.arange(len(labels))
    left = np.zeros(len(labels))
    for (kind, name), col in zip(KINDS, C[:3]):
        vals = np.array([r[name] for r in f1])
        ax.barh(y, vals, left=left, color=col, height=0.68, label=name, edgecolor="white", linewidth=1.0)
        left += vals
    ax.barh(y[-1], left[-1], height=0.68, fill=False, edgecolor=viz_style.INK_2, linewidth=1.0, hatch="///")
    for yi, v in zip(y, left):
        ax.text(v + 0.02, yi, f"{v:.2f}", va="center", fontsize=9.5, color=viz_style.INK_2)
    ax.axvline(1.0, color=viz_style.MUTED, lw=0.8, ls=":")
    ax.set_yticks(y, labels)
    ax.set_xlabel("Dose over one exchange (wrist camera C09 = 1, virtual source)")
    ax.set_xlim(0, left.max() * 1.15)
    ax.grid(axis="x", color=viz_style.GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="center right", bbox_to_anchor=(1.0, 0.36), frameon=False, fontsize=9.5, handlelength=1.2)
    fig.tight_layout()
    _save(fig, "fig1_component_dose")
    plt.close(fig)

    # fig2: B0 대비 변화율 (같은 TCP라도 부품 선량은 달라진다)
    groups = [f"{r['Lever'].replace(' optimization', ' opt.')}\nJ {r['Weighted sum J [%]']:+.1f}%" for r in f2]
    series = [("Wrist camera C09", "Wrist camera C09 [%]", C[0]),
              ("TCP (point-robot model)", "TCP (point-robot model) [%]", C[1])]
    fig, ax = plt.subplots(figsize=(FIG_W, 3.5))
    h = 0.36
    yg = np.arange(len(groups))
    for si, (name, col_key, col) in enumerate(series):
        for gi, r in enumerate(f2):
            v = r[col_key]
            yy = yg[gi] + (si - 0.5) * h
            ax.barh(yy, v, height=h * 0.86, color=col, label=name if gi == 0 else None,
                    edgecolor="white", linewidth=0.8)
            if si == 0 and r["C09 range low [%]"] is not None:
                ax.plot([r["C09 range low [%]"], r["C09 range high [%]"]], [yy, yy], color=viz_style.INK, lw=1.2)
                for xe_ in (r["C09 range low [%]"], r["C09 range high [%]"]):
                    ax.plot([xe_, xe_], [yy - 0.09, yy + 0.09], color=viz_style.INK, lw=1.2)
            txt = f"{v:+.1f}%" if abs(v) >= 0.05 else "0.0% (TCP unchanged)"
            x_txt = min(v, r["C09 range low [%]"] or v) if si == 0 else v
            ax.text(min(x_txt, 0) - 1.5, yy, txt, va="center", ha="right", fontsize=9.5,
                    color=viz_style.INK_2 if si == 0 else col)
    ax.axvline(0, color=viz_style.INK_2, lw=0.8)
    ax.set_yticks(yg, groups)
    ax.invert_yaxis()
    ax.set_xlabel("Dose change vs. B0 (time-optimal baseline) [%]")
    ax.set_xlim(-100, 4)
    ax.grid(axis="x", color=viz_style.GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, handlelength=1.2)
    fig.tight_layout()
    _save(fig, "fig2_levers")
    plt.close(fig)

    # fig3: 설계 방식별 교체 모듈 질량 대 교체 간격 (16, 대표 조건, 부품 매년 교체)
    fig, ax = plt.subplots(figsize=(FIG_W, 3.5))
    x = np.array([r["Exchange interval [days]"] for r in f3])
    m = x <= 20
    cols = {"tcp": C[1], "b0": C[2], "p3_cam": C[0]}
    caps = robot_caps()
    kr120 = next(cap for cap, items in caps if any("KR 120" in n for n, _ in items))
    for (key, name), srow in zip(DESIGNS, f3s):
        yv = np.array([r[name + " [kg]"] for r in f3], float)
        ax.plot(x[m], yv[m], color=cols[key], lw=2.2, label=name)
        t_max = srow["Max interval with KR 120 [days]"]
        if t_max:
            ax.plot([t_max], [kr120], "o", ms=6, color=cols[key], markeredgecolor="white", markeredgewidth=1.0, zorder=5)
            ax.plot([t_max, t_max], [50, kr120], color=cols[key], lw=0.9, ls=":", zorder=1)
            ax.text(t_max + 0.12, 53, f"{t_max:.1f} d", ha="left", va="bottom", fontsize=10, color=cols[key],
                    fontweight="bold")
    for cap, items in caps:
        if cap < 30:
            continue
        ax.axhline(cap, color=viz_style.MUTED, lw=0.9, ls="--", zorder=0)
        ax.text(19.8, cap - 2.5, " / ".join(n for n, _ in items) + f" limit {cap:g} kg", ha="right", va="top",
                fontsize=9.5, color=viz_style.INK_2)
    ax.set_xlim(3, 20)
    ax.set_ylim(50, 260)
    ax.set_xlabel("Exchange interval = bed operating time [days]")
    ax.set_ylabel("Module mass [kg]\n(sorbent + vessel + W shield)")
    ax.grid(True, color=viz_style.GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, handlelength=1.4)
    fig.tight_layout()
    _save(fig, "fig3_exchange")
    plt.close(fig)


def export_tables(f1, f2, f3, f3s):
    """그림 데이터를 CSV와 xlsx(시트별)로 내보낸다. Numbers, Excel에서 차트를 직접 만들 때 쓴다."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    out = OUT / "tables"
    out.mkdir(parents=True, exist_ok=True)
    t1 = [{"Component": r["Component"],
           "Label": f"{r['Component']}  {sum(r[n] for _, n in KINDS):.2f}",
           **{name: (None if r["Component"] == EN_NAME["P0"] else r[name]) for _, name in KINDS},
           "TCP total (point-robot model)": (sum(r[n] for _, n in KINDS) if r["Component"] == EN_NAME["P0"] else None),
           "Total": sum(r[n] for _, n in KINDS)} for r in reversed(f1)]
    t2 = [{"Lever": r["Lever"], "Label": f"{r['Lever']} (J {r['Weighted sum J [%]']:+.1f}%)",
           **{k: v for k, v in r.items() if k not in ("key", "Lever")}} for r in f2]
    t3 = [r for r in f3 if r["Exchange interval [days]"] <= 20]
    tables = [("Fig1_component_dose", t1, "Cumulative dose per exchange task, B0 trajectory, relative to wrist camera C09 = 1 "
                                          "(virtual source, relative values only). Rows sorted from largest to smallest."),
              ("Fig2_levers", t2, "Change in task dose vs. B0 [%]. Camera range = best mount under alternative constraint "
                                  "assumptions (view distance 0.3 to 0.5 m, bracket 6 to 12 cm, 3 or 5 visible points)."),
              ("Fig3_module_mass", t3, "Module mass vs. exchange interval. 0 deg C, 7 bar; fixed wall on the online bed; "
                                       "3-day cooling; robot parts replaced yearly; W shield. Upper-bound source "
                                       "(release fraction 1, no self-shielding or buildup)."),
              ("Fig3_summary", f3s, "Longest exchange interval each robot can handle, per design approach.")]
    wb = Workbook()
    ws0 = wb.active
    ws0.title = "README"
    info = [("E part poster figure data", None),
            ("Generated by", "scripts/14_poster_figures.py (dose-aware-traj)"),
            ("Source files", "outputs/b0, b1, p3 (trajectory CSV), outputs/camera/placement.json, "
                             "outputs/design/design_fine.csv, outputs/poster/poster_numbers.json"),
            ("Note", "Fig1 and Fig2 use a virtual source: compare values only relative to each other. "
                     "Fig3 uses the Xe bed upper-bound source.")]
    info += [(name, note) for name, _, note in tables]
    for i, (a, b) in enumerate(info, start=1):
        ws0.cell(i, 1, a).font = Font(name="Arial", bold=True, size=12 if i == 1 else 10)
        if b:
            ws0.cell(i, 2, b).font = Font(name="Arial", size=10)
            ws0.cell(i, 2).alignment = Alignment(wrap_text=True, vertical="top")
    ws0.column_dimensions["A"].width = 24
    ws0.column_dimensions["B"].width = 110
    head_fill = PatternFill("solid", start_color="F3F6FB")
    for name, rows, note in tables:
        keys = list(rows[0].keys())
        with open(out / f"{name}.csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
        ws = wb.create_sheet(name)
        for j, k in enumerate(keys, start=1):
            c = ws.cell(1, j, k)
            c.font = Font(name="Arial", bold=True, size=10)
            c.fill = head_fill
            c.alignment = Alignment(wrap_text=True, vertical="center")
            ws.column_dimensions[get_column_letter(j)].width = max(14, min(34, len(k) + 2))
        for i, r in enumerate(rows, start=2):
            for j, k in enumerate(keys, start=1):
                v = r[k]
                c = ws.cell(i, j, v)
                c.font = Font(name="Arial", size=10)
                if isinstance(v, float):
                    if "[%]" in k:
                        c.value = v / 100.0
                        c.number_format = "0.0%"
                    elif "[days]" in k:
                        c.number_format = "0.00"
                    elif "[kg]" in k or "[mm]" in k:
                        c.number_format = "0.0"
                    else:
                        c.number_format = "0.000"
        # 합계, 연간 교체 횟수는 수식으로 둔다 (값을 고치면 따라 바뀜)
        if "Total" in keys:
            jt, cols_ = keys.index("Total") + 1, [get_column_letter(keys.index(n) + 1) for _, n in KINDS]
            jtcp = get_column_letter(keys.index("TCP total (point-robot model)") + 1)
            for i, r in enumerate(rows, start=2):
                ws.cell(i, jt).value = (f"={jtcp}{i}" if r["Component"] == EN_NAME["P0"]
                                        else "=" + "+".join(f"{c}{i}" for c in cols_))
        if "Exchanges per year with KR 120" in keys:
            jy = keys.index("Exchanges per year with KR 120") + 1
            jm = get_column_letter(keys.index("Max interval with KR 120 [days]") + 1)
            for i in range(2, len(rows) + 2):
                ws.cell(i, jy).value = f"=365.25/{jm}{i}"
                ws.cell(i, jy).number_format = "0.0"
        ws.row_dimensions[1].height = 32
        ws.freeze_panes = "A2"
    wb.save(out / "E_poster_figure_data.xlsx")
    print(f"표 저장: {out}")


def scene_figure(scene, comps, k09, best):
    """S2 커플링 해제 체류 자세(P3)와 손목 카메라 현재 위치(노랑), 변경 위치(보라, 회색 막대는 브래킷)."""
    import pybullet as p
    from PIL import Image

    steps = task_steps()
    t, seg, q = load_traj("p3")
    s2 = next(i for i, st in enumerate(steps) if st.kind == "dwell" and st.dwell_key == "S2_dwell")
    row = int(np.nonzero(seg == s2)[0][0])
    apply_state(scene, steps[s2].state)
    r = scene.robot
    pos, R = r.link_frames(q[row])
    old = pos[comps[k09].link] + R[comps[k09].link] @ np.asarray(comps[k09].offset, float)
    new = pos[int(best["link"])] + R[int(best["link"])] @ np.asarray(best["offset"], float)
    marks = []
    for x, col in ((old, viz_style.CATEGORICAL[3]), (new, viz_style.CATEGORICAL[6])):
        rgba = [int(col[i:i + 2], 16) / 255 for i in (1, 3, 5)] + [1.0]
        vs = p.createVisualShape(p.GEOM_SPHERE, radius=0.035, rgbaColor=rgba, physicsClientId=scene.cid)
        marks.append(p.createMultiBody(0, -1, vs, x.tolist(), physicsClientId=scene.cid))
    # 브래킷: 장착 링크 표면의 가장 가까운 점에서 카메라까지 막대
    cs = p.createCollisionShape(p.GEOM_SPHERE, radius=0.001, physicsClientId=scene.cid)
    probe = p.createMultiBody(0, cs, -1, new.tolist(), physicsClientId=scene.cid)
    cp = min(p.getClosestPoints(probe, r.id, 0.5, linkIndexB=int(best["link"]), physicsClientId=scene.cid),
             key=lambda c: c[8])
    p.removeBody(probe, physicsClientId=scene.cid)
    a, b = np.asarray(cp[6]), new
    L = float(np.linalg.norm(b - a))
    if L > 1e-3:
        z = (b - a) / L
        ax_ = np.cross([0, 0, 1], z)
        ang = float(np.arccos(np.clip(z[2], -1, 1)))
        quat = p.getQuaternionFromAxisAngle(ax_ / np.linalg.norm(ax_), ang) if np.linalg.norm(ax_) > 1e-9 else [0, 0, 0, 1]
        vs = p.createVisualShape(p.GEOM_CYLINDER, radius=0.01, length=L, rgbaColor=[0.35, 0.35, 0.35, 1],
                                 physicsClientId=scene.cid)
        marks.append(p.createMultiBody(0, -1, vs, ((a + b) / 2).tolist(), quat, physicsClientId=scene.cid))
    img = scene.snapshot(None, q[row], yaw=58, pitch=-20, dist=1.35, target=(0.38, -0.15, 0.62), size=(1500, 1500))
    for b in marks:
        p.removeBody(b, physicsClientId=scene.cid)
    bg = img[0, 0].astype(int)
    diff = np.abs(img.astype(int) - bg).sum(axis=2) > 30
    ys, xs = np.nonzero(diff)
    pad = 20
    crop = img[max(ys.min() - pad, 0):ys.max() + pad, max(xs.min() - pad, 0):xs.max() + pad]
    Image.fromarray(crop).save(OUT / "scene_dwell.png")


if __name__ == "__main__":
    main()
