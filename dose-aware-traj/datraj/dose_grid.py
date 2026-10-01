"""3D 선량률 격자 (dose_grid_*.npy + dose_grid_meta.json) 읽기, 검사, 보간, 저장.

이 파일은 numpy, scipy만 쓰며 다른 모듈에 의존하지 않는다 (방사선 파트에 그대로 전달 가능).

격자 규약 (schema 1.0)
- axis_order = "xyz": array[i, j, k] 는 좌표 (x0 + i*dx, y0 + j*dy, z0 + k*dz) 의 값
- sample_location = "node": origin 은 array[0, 0, 0] 이 놓인 점 (복셀 중심이 아님)
- units = "Gy/h"
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np

SCHEMA_VERSION = "1.0"

REQUIRED_KEYS = [
    "schema_version", "grid_id", "state", "data_file", "dtype", "shape", "axis_order",
    "sample_location", "origin", "spacing", "frame", "layout_version", "quantity",
    "medium", "units", "shielding_included", "sources", "r_min", "version",
    "created_by", "created_at", "method",
]
ALLOWED = {
    "state": {"pre_removal", "post_removal"},
    "axis_order": {"xyz"},
    "sample_location": {"node"},
    "units": {"Gy/h"},
    "quantity": {"absorbed_dose_rate", "air_kerma_rate"},
    "medium": {"Si", "air", "water", "tissue"},
    "dtype": {"float32", "float64"},
    "frame": {"hotcell_world"},
}
# 경로계획에 필요한 최소 범위 (핫셀 내부, z는 1.5 m까지)
REQUIRED_COVERAGE = {"min": [-0.8, -1.0, 0.0], "max": [1.2, 1.0, 1.5]}


def read_meta(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate(meta: dict, arr: np.ndarray | None = None, layout_version: str | None = None):
    """격자와 메타데이터 검사. (errors, warnings) 반환."""
    errors, warns = [], []
    for k in REQUIRED_KEYS:
        if k not in meta:
            errors.append(f"필수 항목 누락: {k}")
    for k, allowed in ALLOWED.items():
        if k in meta and meta[k] not in allowed:
            (warns if k in ("state", "quantity", "medium") else errors).append(
                f"{k} = {meta[k]!r} (허용값: {sorted(allowed)})")
    for k in ("shape", "origin", "spacing"):
        if k in meta and (not isinstance(meta[k], (list, tuple)) or len(meta[k]) != 3):
            errors.append(f"{k}는 길이 3의 리스트여야 합니다")
    if "spacing" in meta and isinstance(meta["spacing"], list) and len(meta["spacing"]) == 3:
        if any(s <= 0 for s in meta["spacing"]):
            errors.append("spacing은 모두 양수여야 합니다")
    if meta.get("schema_version") not in (None, SCHEMA_VERSION):
        warns.append(f"schema_version {meta.get('schema_version')} (현재 {SCHEMA_VERSION})")
    if layout_version and meta.get("layout_version") != layout_version:
        warns.append(f"layout_version 불일치: 격자 {meta.get('layout_version')} / 배치도 {layout_version}")
    if not meta.get("sources"):
        warns.append("sources가 비어 있습니다. 이동 선원(S3) 계산과 축 방향 점검에 필요합니다")

    if arr is not None:
        if list(arr.shape) != list(meta.get("shape", [])):
            errors.append(f"배열 shape {list(arr.shape)} 와 meta shape {meta.get('shape')} 불일치")
        if str(arr.dtype) != meta.get("dtype"):
            errors.append(f"배열 dtype {arr.dtype} 와 meta dtype {meta.get('dtype')} 불일치")
        if not np.all(np.isfinite(arr)):
            errors.append(f"NaN 또는 inf 값 {int(np.sum(~np.isfinite(arr)))}개")
        elif np.any(arr < 0):
            errors.append(f"음수 값 {int(np.sum(arr < 0))}개 (선량률은 0 이상)")

    # 범위 점검
    if not errors or all("범위" not in e for e in errors):
        try:
            lo = np.asarray(meta["origin"], float)
            hi = lo + np.asarray(meta["spacing"], float) * (np.asarray(meta["shape"]) - 1)
            need_lo = np.asarray(REQUIRED_COVERAGE["min"])
            need_hi = np.asarray(REQUIRED_COVERAGE["max"])
            if np.any(lo > need_lo + 1e-9) or np.any(hi < need_hi - 1e-9):
                errors.append(
                    f"격자 범위 {np.round(lo, 3).tolist()} ~ {np.round(hi, 3).tolist()} 가 "
                    f"필요 범위 {REQUIRED_COVERAGE['min']} ~ {REQUIRED_COVERAGE['max']} 를 덮지 못합니다")
        except (KeyError, TypeError, ValueError):
            pass

    # 축 순서 점검: 최댓값 위치가 선원 근처인지
    if arr is not None and not errors and meta.get("sources"):
        idx = np.unravel_index(int(np.argmax(arr)), arr.shape)
        p_max = np.asarray(meta["origin"]) + np.asarray(meta["spacing"]) * np.asarray(idx)
        src_pts = []
        for s in meta["sources"]:
            for key in ("position", "start", "end"):
                if key in s:
                    src_pts.append(s[key])
            src_pts.extend(s.get("points", []))
        if src_pts:
            dmin = float(np.min(np.linalg.norm(np.asarray(src_pts) - p_max, axis=1)))
            seg_tol = 0.5
            if dmin > seg_tol:
                warns.append(
                    f"최댓값 위치 {np.round(p_max, 3).tolist()} 가 선원 기준점에서 {dmin:.2f} m 떨어져 있습니다. "
                    "axis_order 또는 origin이 어긋났을 수 있습니다")
    return errors, warns


@dataclass
class DoseGrid:
    values: np.ndarray
    meta: dict

    @classmethod
    def load(cls, npy_path: str | Path, meta_path: str | Path | None = None,
             strict: bool = True) -> "DoseGrid":
        npy_path = Path(npy_path)
        if meta_path is None:
            meta_path = npy_path.with_name(npy_path.stem + "_meta.json")
        meta = read_meta(meta_path)
        arr = np.load(npy_path)
        errors, warns = validate(meta, arr)
        if errors and strict:
            raise ValueError("격자 검사 실패:\n  - " + "\n  - ".join(errors))
        for w in warns:
            print(f"[DoseGrid 경고] {npy_path.name}: {w}")
        return cls(arr, meta)

    @property
    def origin(self) -> np.ndarray:
        return np.asarray(self.meta["origin"], float)

    @property
    def spacing(self) -> np.ndarray:
        return np.asarray(self.meta["spacing"], float)

    @property
    def shape(self) -> tuple:
        return tuple(self.values.shape)

    @property
    def axes(self) -> list[np.ndarray]:
        return [self.origin[i] + self.spacing[i] * np.arange(self.shape[i]) for i in range(3)]

    @property
    def bounds(self) -> tuple[np.ndarray, np.ndarray]:
        lo = self.origin
        return lo, lo + self.spacing * (np.asarray(self.shape) - 1)

    def __call__(self, points, warn_outside: bool = True) -> np.ndarray:
        """3선형 보간 선량률 (Gy/h). 격자 밖 점은 경계로 잘라 쓴다."""
        P = np.asarray(points, float)
        flat = P.reshape(-1, 3)
        lo, hi = self.bounds
        outside = np.any((flat < lo - 1e-9) | (flat > hi + 1e-9), axis=1)
        if warn_outside and outside.any():
            print(f"[DoseGrid 경고] 격자 밖 점 {int(outside.sum())}개를 경계 값으로 처리했습니다")
        f = (np.clip(flat, lo, hi) - lo) / self.spacing
        i0 = np.minimum(np.floor(f).astype(int), np.asarray(self.shape) - 2)
        i0 = np.maximum(i0, 0)
        t = f - i0
        V = self.values
        x0, y0, z0 = i0[:, 0], i0[:, 1], i0[:, 2]
        tx, ty, tz = t[:, 0], t[:, 1], t[:, 2]
        c000 = V[x0, y0, z0]; c100 = V[x0 + 1, y0, z0]
        c010 = V[x0, y0 + 1, z0]; c110 = V[x0 + 1, y0 + 1, z0]
        c001 = V[x0, y0, z0 + 1]; c101 = V[x0 + 1, y0, z0 + 1]
        c011 = V[x0, y0 + 1, z0 + 1]; c111 = V[x0 + 1, y0 + 1, z0 + 1]
        c00 = c000 * (1 - tx) + c100 * tx
        c10 = c010 * (1 - tx) + c110 * tx
        c01 = c001 * (1 - tx) + c101 * tx
        c11 = c011 * (1 - tx) + c111 * tx
        c0 = c00 * (1 - ty) + c10 * ty
        c1 = c01 * (1 - ty) + c11 * ty
        out = c0 * (1 - tz) + c1 * tz
        return out.reshape(P.shape[:-1])

    def slice(self, axis: str, value: float):
        """axis 방향 좌표 value에서의 단면 (보간). (가로축, 세로축, 2D 값) 반환."""
        ax = "xyz".index(axis)
        others = [i for i in range(3) if i != ax]
        A, B = self.axes[others[0]], self.axes[others[1]]
        AA, BB = np.meshgrid(A, B, indexing="ij")
        pts = np.zeros(AA.shape + (3,))
        pts[..., others[0]] = AA
        pts[..., others[1]] = BB
        pts[..., ax] = value
        return A, B, self(pts, warn_outside=False)


def make_meta(*, grid_id: str, state: str, data_file: str, arr: np.ndarray, origin, spacing,
              sources: list[dict], layout_version: str, medium: str = "Si",
              shielding_included: bool = False, r_min: float = 0.05, version: str = "v0",
              created_by: str = "", method: str = "", notes: str = "",
              quantity: str = "absorbed_dose_rate") -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "grid_id": grid_id,
        "state": state,
        "data_file": data_file,
        "dtype": str(arr.dtype),
        "shape": list(arr.shape),
        "axis_order": "xyz",
        "sample_location": "node",
        "origin": [float(v) for v in origin],
        "spacing": [float(v) for v in spacing],
        "frame": "hotcell_world",
        "layout_version": layout_version,
        "quantity": quantity,
        "medium": medium,
        "units": "Gy/h",
        "shielding_included": bool(shielding_included),
        "sources": sources,
        "r_min": float(r_min),
        "version": version,
        "created_by": created_by,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "method": method,
        "notes": notes,
    }


def save(arr: np.ndarray, meta: dict, out_dir: str | Path) -> tuple[Path, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    npy = out_dir / meta["data_file"]
    meta_path = npy.with_name(npy.stem + "_meta.json")
    np.save(npy, arr)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return npy, meta_path
