"""선량 격자 파일 점검 도구.

사용법
    python check_dose_grid.py dose_grid_pre.npy
    python check_dose_grid.py dose_grid_pre.npy --layout hotcell_layout.json --out quicklook_pre.png

하는 일
1. <이름>_meta.json 을 읽어 필수 항목, 허용값, 배열 shape/dtype, NaN/음수, 격자 범위를 검사
2. 최댓값 위치가 선원 근처인지 확인 (axis_order, origin 실수 탐지)
3. 단면 그림(quicklook) 저장: 선원 표시(빨간 점선)가 배치도의 베드·배관 위에 겹쳐야 정상
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
try:
    from datraj.dose_grid import DoseGrid, read_meta, validate
    from datraj.layout_plot import draw_layout, draw_sources
    from datraj import viz_style
    DEFAULT_LAYOUT = HERE.parent / "config" / "hotcell_layout.json"
except ImportError:  # 인계 폴더에서 단독 실행
    from dose_grid import DoseGrid, read_meta, validate
    from layout_plot import draw_layout, draw_sources
    import viz_style
    DEFAULT_LAYOUT = HERE / "hotcell_layout.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("npy")
    ap.add_argument("--meta", default=None)
    ap.add_argument("--layout", default=str(DEFAULT_LAYOUT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    npy = Path(args.npy)
    meta_path = Path(args.meta) if args.meta else npy.with_name(npy.stem + "_meta.json")
    if not meta_path.exists():
        print(f"[오류] 메타데이터 파일이 없습니다: {meta_path}")
        return 1
    meta = read_meta(meta_path)
    arr = np.load(npy)
    layout = None
    if args.layout and Path(args.layout).exists():
        with open(args.layout, encoding="utf-8") as f:
            layout = json.load(f)
    errors, warns = validate(meta, arr, layout["layout_version"] if layout else None)

    print(f"파일        : {npy.name} / {meta_path.name}")
    print(f"grid_id     : {meta.get('grid_id')}  (state={meta.get('state')}, version={meta.get('version')})")
    print(f"shape       : {list(arr.shape)}  dtype={arr.dtype}")
    if "origin" in meta and "spacing" in meta:
        lo = np.asarray(meta["origin"])
        hi = lo + np.asarray(meta["spacing"]) * (np.asarray(arr.shape) - 1)
        print(f"범위 [m]    : x {lo[0]:.3f}~{hi[0]:.3f}, y {lo[1]:.3f}~{hi[1]:.3f}, z {lo[2]:.3f}~{hi[2]:.3f}")
        print(f"간격 [m]    : {np.round(meta['spacing'], 4).tolist()}")
    if np.all(np.isfinite(arr)):
        print(f"값 [{meta.get('units')}] : min {arr.min():.3e}, median {np.median(arr):.3e}, max {arr.max():.3e}")
    for e in errors:
        print(f"[오류] {e}")
    for w in warns:
        print(f"[경고] {w}")
    print("결과        :", "통과" if not errors else f"실패 ({len(errors)}건)")

    if errors:
        return 1

    viz_style.apply()
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm

    grid = DoseGrid(arr, meta)
    srcs = meta.get("sources", [])
    # 단면 위치: 첫 번째 선원을 지나도록
    ref = np.asarray(srcs[0].get("start", srcs[0].get("position", [0.5, -0.28, 0.25]))) if srcs else np.array([0.5, -0.28, 0.25])
    if "end" in (srcs[0] if srcs else {}):
        ref = (np.asarray(srcs[0]["start"]) + np.asarray(srcs[0]["end"])) / 2
    cuts = [("z", ref[2], "xy"), ("y", ref[1], "xz"), ("x", ref[0], "yz")]
    vmax = float(arr.max())
    vmin = max(vmax * 1e-4, float(arr[arr > 0].min()) if np.any(arr > 0) else 1e-12)
    fig, axs = plt.subplots(1, 3, figsize=(15, 5.2))
    state = "pre_removal" if meta.get("state") == "pre_removal" else "post_removal"
    im = None
    for ax, (axis, val, plane) in zip(axs, cuts):
        A, B, V = grid.slice(axis, val)
        im = ax.pcolormesh(A, B, np.clip(V.T, vmin, None), cmap=viz_style.DOSE_CMAP,
                           norm=LogNorm(vmin=vmin, vmax=vmax), shading="auto", zorder=1)
        if layout:
            draw_layout(ax, layout, plane, state=state)
        draw_sources(ax, srcs, plane)
        ax.set_title(f"{axis} = {val:.2f} m 단면", loc="left")
    cb = fig.colorbar(im, ax=axs, shrink=0.85, pad=0.01)
    cb.set_label(f"선량률 [{meta.get('units')}]")
    fig.suptitle(f"{meta.get('grid_id')}  |  빨간 점선 = meta의 선원 위치. 배치도의 베드·배관과 겹치면 축 방향이 맞습니다",
                 x=0.01, ha="left", fontsize=10, color=viz_style.INK_2)
    out = Path(args.out) if args.out else npy.with_name(npy.stem + "_quicklook.png")
    fig.savefig(out)
    print(f"단면 그림   : {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
