"""부품 단위 설계(체류 자세, 카메라 배치)가 Xe 베드 교체 차폐, 모듈 질량, 로봇 선택에 주는 영향.

11은 B0 궤적, 기본 카메라 위치의 부품 단위 선량으로 필요 차폐와 모듈 질량을 구했다.
여기서는 같은 Xe 베드 상한 선원, 같은 시나리오 표(11의 scenario_rows)를 설계 방식만 바꿔 다시 푼다.

설계 방식
- TCP 기준 (점 로봇): 모든 부품이 TCP 선량을 받는다고 보고 부품별 예산과 비교 (B0 궤적).
  결국 TCP 선량과 가장 약한 부품(C09) 예산의 비교가 된다
- 부품 기준 B0: 11과 같음
- 부품 기준 P3: 체류 자세 최적화 궤적 (13)
- 부품 기준 B0 + 카메라 배치, P3 + 카메라 배치: 15에서 찾은 장착 가능 위치 (궤적별 전체 최적)

필요 차폐는 max_k D_k(x) / 예산_k <= 1 로 정해지므로, 어느 부품이 이 최대값을 정하는지(제한 부품)가 핵심이다.

실행: python scripts/16_design_to_shield.py        (06, 11, 13, 15를 먼저 실행)
출력: outputs/design/ unit_dose_designs.csv, design_rows.csv, design_fine.csv, summary_design.json
"""
import copy
import csv
import importlib
import json
import math
from dataclasses import replace

import numpy as np

import _bootstrap  # noqa: F401
from datraj import OUTPUTS, config
from datraj import xe_bed as X
from datraj.components import load as load_components
from datraj.dose_eval import ComponentDoseEvaluator, build_fields
from datraj.scene import Scene
from datraj.task import task_steps

xe11 = importlib.import_module("11_xe_bed_budget")   # 파일명이 숫자로 시작해서 import 문 대신 사용
DAY = 86400.0
KEY = {"condition": "0 °C, 7 bar", "B_fixed_shield": True, "t_c_d": 3, "material": "W"}   # 10/11 분석의 성립 조건
TON_FINE = [float(x) for x in np.arange(3.25, 30.001, 0.25)]   # 대표 조건에서 교체 간격을 0.25일 간격으로 [일] (그림·표가 등간격)


def load_traj(tag):
    with open(OUTPUTS / tag / f"traj_{tag}.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    t = np.array([float(r["t"]) for r in rows])
    seg = np.array([int(r["segment"]) for r in rows])
    q = np.array([[float(r[f"q_A{j}"]) for j in range(1, 8)] for r in rows])
    return t, seg, q


def unit_doses(scene, comps, tag):
    """궤적 CSV로 선원별(bed_A, bed_B) 세기 1 Gy/h@1m 당 부품 누적선량 [Gy]. 11의 unit_doses와 같은 정의."""
    steps = task_steps()
    t, seg, q = load_traj(tag)
    ev = ComponentDoseEvaluator(scene.robot, comps)
    P, tcp, R = ev.positions(q)
    base = config.virtual_sources()
    out = {}
    for sid in ("bed_A", "bed_B"):
        vs = copy.deepcopy(base)
        for s in vs["sources"]:
            s["strength"] = 1.0 if s["id"] == sid else 0.0
        fields = build_fields("model", sources=vs)
        tot = np.zeros(len(comps))
        for s in range(seg.max() + 1):
            idx = np.nonzero(seg == s)[0]
            if s > 0:
                idx = np.concatenate([[idx[0] - 1], idx])
            r = fields[steps[s].field].rate(P[idx], tcp[idx], R[idx], t[idx]) * ev.S[None, :]
            tot += np.trapezoid(r, t[idx], axis=0) / 3600.0
        out[sid] = tot
    return out


def t_on_ranges(fine, cfg):
    """로봇마다 모듈 질량(부품 매년 교체)이 허용 하중 이하인 교체 간격 [일]의 [최소, 최대]. 없으면 None.

    모듈 질량이 교체 간격에 대해 단조 증가하면 최대값은 허용 하중과 만나는 점을 선형 보간한 값,
    아니면 격자에서 조건을 만족하는 가장 큰 간격.
    """
    out = {}
    T = np.array([r["T_on_d"] for r in fine], float)
    M = np.array([np.nan if r["module_kg_yearly_parts"] is None else r["module_kg_yearly_parts"] for r in fine], float)
    for rb in cfg["robots"]["candidates"]:
        cap = min(rb["rated_kg"], rb["envelope_kg"] or rb["rated_kg"])
        ok = T[M <= cap]
        if not len(ok):
            out[rb["id"]] = None
            continue
        hi = float(ok.max())
        i = int(np.nonzero(T == hi)[0][0])
        if np.all(np.diff(M) > 0) and i + 1 < len(T):
            hi = float(np.interp(cap, M[i:i + 2], T[i:i + 2]))
        out[rb["id"]] = [float(ok.min()), round(hi, 2)]
    return out


def main():
    cfg = X.load()
    out = OUTPUTS / "design"
    out.mkdir(parents=True, exist_ok=True)
    comps, _ = load_components()
    real = [k for k, c in enumerate(comps) if not c.reference]
    kT = next(k for k, c in enumerate(comps) if c.reference)
    k09 = next(k for k, c in enumerate(comps) if c.id == "C09")
    ids = [comps[k].id for k in real]
    bud = cfg["budget"]
    fail = np.array([bud["TID_fail_Gy"].get(i) if bud["TID_fail_Gy"].get(i) is not None else np.nan for i in ids], float)
    tid_lim = fail / bud["RDM"]
    life_s = bud["life_EFPY"] * 365.25 * DAY
    place = json.load(open(OUTPUTS / "camera" / "placement.json", encoding="utf-8"))

    def cam_comps(tag):
        b = place[tag]["best"]
        c2 = list(comps)
        c2[k09] = replace(comps[k09], link=int(b["link"]), offset=np.asarray(b["offset"], float))
        return c2, b

    scene = Scene()
    U = {"b0": unit_doses(scene, comps, "b0"), "p3": unit_doses(scene, comps, "p3")}
    cb0, best_b0 = cam_comps("b0")
    cp3, best_p3 = cam_comps("p3")
    U["b0_cam"] = unit_doses(scene, cb0, "b0")
    U["p3_cam"] = unit_doses(scene, cp3, "p3")

    # 11과 같은 정의인지 확인 (B0, 기본 카메라)
    with open(OUTPUTS / "xe_bed" / "unit_dose.csv", encoding="utf-8") as f:
        ref = {r["component"]: (float(r["d_bedA_Gy_per_GyPerHourAt1m"]), float(r["d_bedB"])) for r in csv.DictReader(f)}
    err = max(abs(U["b0"][s][k] / ref[comps[k].id][j] - 1) for k in real for j, s in enumerate(("bed_A", "bed_B")))
    print(f"11 단위 선량과 상대 차이 최대 {err:.2e}")
    assert err < 1e-3, "궤적 CSV 재적분이 11 단위 선량과 다름"

    designs = [
        ("tcp", "TCP 기준 (점 로봇)", "b0", lambda u: np.full(len(real), u[kT])),
        ("b0", "부품 기준 B0", "b0", lambda u: u[real]),
        ("p3", "부품 기준 P3 (체류 자세)", "p3", lambda u: u[real]),
        ("b0_cam", "부품 기준 B0 + 카메라 배치", "b0_cam", lambda u: u[real]),
        ("p3_cam", "부품 기준 P3 + 카메라 배치", "p3_cam", lambda u: u[real]),
    ]
    rows_all, fine_all, summ = [], [], {"note": "Xe 베드 상한 선원(11과 같은 가정). TID_lim = 문헌 고장선량 / RDM 2. C10은 값이 없어 제외",
                          "check_vs_11_max_rel_err": err, "key_scenario": KEY,
                          "camera_b0": best_b0, "camera_p3": best_p3, "designs": {}}
    with open(out / "unit_dose_designs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["design", "component", "d_bedA", "d_bedB", "TID_lim_Gy", "ratio_bedA_per_budget"])
        for key, name, src, pick in designs:
            dA, dB = pick(U[src]["bed_A"]), pick(U[src]["bed_B"])
            for j, k in enumerate(real):
                w.writerow([key, comps[k].id, f"{dA[j]:.6e}", f"{dB[j]:.6e}",
                            "" if math.isnan(tid_lim[j]) else f"{tid_lim[j]:.2f}",
                            "" if math.isnan(tid_lim[j]) else f"{dA[j] / tid_lim[j]:.6e}"])
            rows = xe11.scenario_rows(cfg, dA, dB, tid_lim, life_s)
            for r in rows:
                r["design"] = key
            rows_all += rows
            fine = [r for r in xe11.scenario_rows(cfg, dA, dB, tid_lim, life_s, conditions=[("0 °C, 7 bar", 0.0, 7.0)],
                                                  t_on_days=TON_FINE, t_c_days=[KEY["t_c_d"]], b_fixed_opts=(True,),
                                                  c2=False) if r["material"] == "W"]
            for r in fine:
                r["design"] = key
            fine_all += fine
            # 제한 부품: 운전 베드 차폐벽이 있을 때(B 기여 0) Bed A 단위 선량 / 예산이 가장 큰 부품
            ra = dA / tid_lim
            order = np.argsort(-np.nan_to_num(ra, nan=-1))
            c1w = [r for r in rows if r["concept"].startswith("C1") and r["material"] == "W"]
            key_rows = sorted([r for r in rows if all(r[a] == v for a, v in KEY.items()) and r["concept"].startswith("C1")],
                              key=lambda r: r["T_on_d"])
            summ["designs"][key] = {
                "name": name,
                "limiting_bedA": [{"id": ids[i], "ratio": float(ra[i]), "rel_to_b0_C09": None} for i in order[:3]],
                "worst_ratio_bedA": float(np.nanmax(ra)),
                "C1_W_rows": len(c1w),
                "C1_W_robot_ok": sum(1 for r in c1w if r["robots_ok"]),
                "C1_W_robot_ok_yearly_parts": sum(1 for r in c1w if r["robots_ok_yearly_parts"]),
                "T_on_range_by_robot_yearly_parts": t_on_ranges(fine, cfg),
                "key_rows": [{k: r[k] for k in ("T_on_d", "N_ex", "x_req_mm", "module_kg", "robots_ok",
                                                "x_req_mm_yearly_parts", "module_kg_yearly_parts",
                                                "robots_ok_yearly_parts")} for r in key_rows],
            }
    w0 = summ["designs"]["b0"]["worst_ratio_bedA"]
    for d in summ["designs"].values():
        d["worst_ratio_rel_b0"] = d["worst_ratio_bedA"] / w0
        for lim in d["limiting_bedA"]:
            lim["rel_to_b0_C09"] = lim["ratio"] / w0

    # 성립하는 조건 조합 (C1, W): 설계별로 로봇 직접 교체가 되는 (조건, 차폐벽, 냉각, 부품 교체) 조합
    for key, *_ in designs:
        feas = set()
        for r in rows_all:
            if r["design"] != key or not r["concept"].startswith("C1") or r["material"] != "W":
                continue
            for yearly, col in ((False, "robots_ok"), (True, "robots_ok_yearly_parts")):
                if r[col]:
                    feas.add((r["condition"], r["B_fixed_shield"], r["t_c_d"], yearly))
        summ["designs"][key]["feasible_condition_sets"] = sorted(
            [{"condition": c, "B_fixed": b, "t_c_d": t, "yearly_parts": y} for c, b, t, y in feas],
            key=lambda z: (z["condition"], z["B_fixed"], z["t_c_d"], z["yearly_parts"]))

    with open(out / "design_rows.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=["design"] + [k for k in rows_all[0] if k != "design"])
        wr.writeheader()
        wr.writerows(rows_all)
    with open(out / "design_fine.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=["design"] + [k for k in fine_all[0] if k != "design"])
        wr.writeheader()
        wr.writerows(fine_all)
    with open(out / "summary_design.json", "w", encoding="utf-8") as f:
        json.dump(summ, f, ensure_ascii=False, indent=1)

    print("\n설계 방식별 제한 부품 (운전 베드 차폐벽 있음, Bed A 단위 선량 / 예산, 부품 기준 B0 = 1)")
    for key, d in summ["designs"].items():
        lim = ", ".join(f"{x['id']} {x['rel_to_b0_C09']:.2f}" for x in d["limiting_bedA"])
        print(f"  {d['name']:24s} 최대 {d['worst_ratio_rel_b0']:.2f}  (상위: {lim})  "
              f"C1·W 로봇 직접 교체 성립 {d['C1_W_robot_ok']}/{d['C1_W_rows']}, 부품 매년 교체 시 {d['C1_W_robot_ok_yearly_parts']}")
    print(f"\n대표 조건 {KEY} 에서 교체 간격별 W 두께 [mm] / 모듈 질량 [kg] / 가능 로봇 (부품 매년 교체)")
    for key, d in summ["designs"].items():
        cells = [f"{r['T_on_d']:g}d: {r['x_req_mm_yearly_parts']}/{r['module_kg_yearly_parts']}/{r['robots_ok_yearly_parts'] or '-'}"
                 for r in d["key_rows"]]
        print(f"  {d['name']:24s} " + " | ".join(cells))
    print(f"\n대표 조건, 부품 매년 교체: 로봇별로 감당할 수 있는 교체 간격 [일] (촘촘한 간격 {TON_FINE[0]}~{TON_FINE[-1]}일)")
    for key, d in summ["designs"].items():
        cells = [f"{rid}: " + (f"{v[0]:.1f}~{v[1]:.1f}" if v else "없음") for rid, v in d["T_on_range_by_robot_yearly_parts"].items()]
        print(f"  {d['name']:24s} " + " | ".join(cells))
    print(f"\n출력 폴더: {out}")


if __name__ == "__main__":
    main()
