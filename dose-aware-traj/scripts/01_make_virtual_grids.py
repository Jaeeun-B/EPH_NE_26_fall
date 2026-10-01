"""가상 선량 격자 생성 (방사선 파트 격자가 오기 전까지 사용).

config/virtual_sources.json 의 선원으로 베드 제거 전/후 격자를 만든다.
격자 범위는 핫셀 내부 전체, 해상도는 축마다 N개 노드 (기본 25, 50, 100).

실행: python scripts/01_make_virtual_grids.py [--n 25 50 100]
출력: data/dose_grids/dose_grid_{pre,post}_N{n}.npy + _meta.json
"""
import argparse

import numpy as np

import _bootstrap  # noqa: F401
from datraj import GRID_DIR, config
from datraj import dose_grid as dg
from datraj.dose_model import grid_from_sources, sources_from_dicts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, nargs="+", default=[25, 50, 100])
    args = ap.parse_args()

    layout = config.layout()
    vs = config.virtual_sources()
    lo = np.asarray(layout["cell"]["interior_min"], float)
    hi = np.asarray(layout["cell"]["interior_max"], float)
    by_id = {s["id"]: s for s in vs["sources"]}

    for state, short in (("pre_removal", "pre"), ("post_removal", "post")):
        src_dicts = [dict(by_id[i], r_min=vs["r_min"]) for i in vs["states"][state]]
        sources = sources_from_dicts(src_dicts, vs["r_min"])
        for n in args.n:
            shape = (n, n, n)
            spacing = (hi - lo) / (n - 1)
            arr = grid_from_sources(sources, lo, spacing, shape).astype(np.float32)
            meta = dg.make_meta(
                grid_id=f"virtual_{short}_N{n}", state=state,
                data_file=f"dose_grid_{short}_N{n}.npy", arr=arr, origin=lo, spacing=spacing,
                sources=src_dicts, layout_version=layout["layout_version"], medium=vs["medium"],
                r_min=vs["r_min"], version="v0-virtual", created_by="E part (virtual)",
                method="analytic point/line kernel 1/r^2, no shielding (datraj.dose_model)",
                notes="가상 선원. 절대값 의미 없음. 방사선 파트 격자로 교체 예정.")
            errors, warns = dg.validate(meta, arr, layout["layout_version"])
            assert not errors, errors
            npy, mp = dg.save(arr, meta, GRID_DIR)
            print(f"{npy.relative_to(GRID_DIR.parent.parent)}  shape={shape}  "
                  f"spacing={spacing[0]:.4f} m  max={arr.max():.3g} Gy/h")


if __name__ == "__main__":
    main()
