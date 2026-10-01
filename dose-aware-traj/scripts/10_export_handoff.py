"""다른 파트에 넘길 인계 파일을 handoff/ 폴더에 만든다.

실행: python scripts/10_export_handoff.py
  01_radiation : 선량 격자 규격, 메타데이터 양식, 가상 격자 샘플, dose_model.py, 점검 도구
  02_layout    : 핫셀 좌표계·배치 초안 (json + 그림)
  03_materials : 부품별 차폐·TID 입력 양식 (xlsx) + 부품 위치도
  04_control   : 공통 파라미터 (2관절 축약 모델 포함), e_track 양식
README.md 는 handoff/ 각 폴더에 미리 작성되어 있다.
"""
import csv
import json
import shutil
import subprocess
import sys

import numpy as np
import pybullet as p

import _bootstrap  # noqa: F401
from datraj import CONFIG, GRID_DIR, ROOT, config, viz_style
from datraj import dose_grid as dg
from datraj.components import load as load_components
from datraj.handoff_build import build_materials_xlsx, draw_component_figure, reduced_2dof
from datraj.layout_plot import draw_layout, draw_sources
from datraj.robot import Robot

H = ROOT / "handoff"


def radiation(layout):
    d = H / "01_radiation"
    (d / "sample").mkdir(parents=True, exist_ok=True)
    for f in ("dose_model.py", "dose_grid.py", "layout_plot.py", "viz_style.py"):
        shutil.copy(ROOT / "datraj" / f, d / f)
    shutil.copy(ROOT / "scripts" / "check_dose_grid.py", d / "check_dose_grid.py")
    shutil.copy(CONFIG / "hotcell_layout.json", d / "hotcell_layout.json")
    for short in ("pre", "post"):
        stem = f"dose_grid_{short}_N50"
        src_npy = GRID_DIR / f"{stem}.npy"
        if not src_npy.exists():
            raise SystemExit("먼저 python scripts/01_make_virtual_grids.py 를 실행하세요")
        arr = np.load(src_npy)
        meta = dg.read_meta(GRID_DIR / f"{stem}_meta.json")
        name = f"dose_grid_{short}"
        meta["data_file"] = f"{name}.npy"
        meta["grid_id"] = f"sample_virtual_{short}"
        npy, _ = dg.save(arr, meta, d / "sample")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "check_dose_grid.py"), str(npy),
                        "--out", str(d / "sample" / f"{name}_quicklook.png")], check=True, capture_output=True)

    template = {
        "schema_version": "1.0",
        "grid_id": "rad_pre_v1",
        "state": "pre_removal",
        "data_file": "dose_grid_pre.npy",
        "dtype": "float32",
        "shape": [100, 100, 100],
        "axis_order": "xyz",
        "sample_location": "node",
        "origin": [-0.8, -1.0, 0.0],
        "spacing": [0.020202, 0.020202, 0.020202],
        "frame": "hotcell_world",
        "layout_version": layout["layout_version"],
        "quantity": "absorbed_dose_rate",
        "medium": "Si",
        "units": "Gy/h",
        "shielding_included": False,
        "sources": [
            {"id": "bed_A", "kind": "line", "start": [0.50, -0.28, 0.07], "end": [0.50, -0.28, 0.43],
             "strength": 0.0, "nuclides": [{"name": "Kr-85", "activity_Bq": 0.0}],
             "note": "strength = 1 m 거리 점선원으로 봤을 때의 선량률 [Gy/h]. 핵종 구성과 근거를 note에"}
        ],
        "r_min": 0.05,
        "version": "v1",
        "created_by": "방사선 파트 (이름)",
        "created_at": "YYYY-MM-DD HH:MM",
        "method": "계산 방법 (예: 점커널 해석식, OpenMC 등)",
        "notes": "가정, 교체 시점, 반영한 핵종, 제동복사 반영 여부 등",
    }
    with open(d / "dose_grid_meta_template.json", "w", encoding="utf-8") as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    print("01_radiation 완료")


def layout_figure(layout, out):
    viz_style.apply()
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle

    vs = config.virtual_sources()
    srcs = [s for s in vs["sources"] if s["id"] in vs["states"]["pre_removal"]]
    fig, axs = plt.subplots(1, 3, figsize=(15, 5.4), gridspec_kw={"width_ratios": [1, 1, 1]})
    for ax, plane in zip(axs, ("xy", "xz", "yz")):
        draw_layout(ax, layout, plane, state="pre_removal")
        draw_sources(ax, srcs, plane)
        ax.grid(True)
        ax.set_axisbelow(True)
    axs[0].add_patch(Circle((0, 0), 0.82, fill=False, ec=viz_style.MUTED, lw=0.8, ls=":"))
    axs[0].text(0.0, 0.84, "0.82 m (iiwa 14 도달거리)", ha="center", va="bottom", fontsize=7, color=viz_style.MUTED)
    axs[0].annotate("", xy=(0.25, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=viz_style.INK, lw=1.2))
    axs[0].annotate("", xy=(0, 0.25), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=viz_style.INK, lw=1.2))
    axs[0].text(0.27, 0, "x", va="center", fontsize=9)
    axs[0].text(0, 0.27, "y", ha="center", fontsize=9)
    axs[0].set_title("위에서 본 모습 (xy)", loc="left")
    axs[1].set_title("옆에서 본 모습 (xz)", loc="left")
    axs[2].set_title("앞에서 본 모습 (yz)", loc="left")
    fig.suptitle(f"핫셀 배치 초안 {layout['layout_version']}  |  원점 = 로봇 베이스 바닥 중심, 단위 m, "
                 "빨간 점선 = 가상 선원 위치", x=0.01, ha="left", fontsize=10, color=viz_style.INK_2)
    fig.savefig(out)
    plt.close(fig)


def layout_part(layout):
    d = H / "02_layout"
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy(CONFIG / "hotcell_layout.json", d / "hotcell_layout.json")
    layout_figure(layout, d / "hotcell_layout.png")
    print("02_layout 완료")


def materials(robot):
    d = H / "03_materials"
    d.mkdir(parents=True, exist_ok=True)
    comps, _ = load_components(xlsx_path=CONFIG / "__none__.xlsx")
    q_fig = np.array([0.0, 0.55, 0.0, -1.35, 0.0, 0.95, 0.0])
    fig = d / "component_locations.png"
    draw_component_figure(robot, comps, q_fig, fig)
    build_materials_xlsx(comps, d / "component_inputs.xlsx", fig)
    print("03_materials 완료 (수식은 Excel에서 열 때 계산됨)")


def control(robot, params):
    d = H / "04_control"
    d.mkdir(parents=True, exist_ok=True)
    params = json.loads(json.dumps(params))
    params["reduced_2dof"] = reduced_2dof(robot, params)
    # 저장소의 원본에도 반영 (두 모델이 같은 파일을 쓰도록)
    config.save_json(params, CONFIG / "shared_params.json")
    shutil.copy(CONFIG / "shared_params.json", d / "shared_params.json")
    cases = params["inclination_envelope"]["cases"]
    with open(d / "e_track_template.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "roll_deg", "pitch_deg", "payload", "e_track_max_m", "e_track_rms_m",
                    "settling_time_s", "note"])
        for c in cases:
            for payload in ("none", "spent_bed"):
                w.writerow([c["id"], c["roll_deg"], c["pitch_deg"], payload, "", "", "", ""])
    b0 = ROOT / "outputs" / "b0"
    copied = []
    for f in ("traj_b0.csv", "traj_b0_A2A4.csv"):
        if (b0 / f).exists():
            shutil.copy(b0 / f, d / f)
            copied.append(f)
    print("04_control 완료" + (f" (B0 궤적 포함: {', '.join(copied)})" if copied else
                               " (B0 궤적 없음: scripts/06_run_b0.py 먼저 실행)"))


def main():
    layout = config.layout()
    params = config.shared_params()
    cid = p.connect(p.DIRECT)
    robot = Robot(cid, params, layout["robot"]["base_position"], layout["robot"]["base_rpy"])
    radiation(layout)
    layout_part(layout)
    materials(robot)
    control(robot, params)
    p.disconnect(cid)


if __name__ == "__main__":
    main()
