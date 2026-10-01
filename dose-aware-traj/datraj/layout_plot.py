"""핫셀 배치도 그리기 (위에서 본 xy, 옆에서 본 xz / yz 투영). numpy, matplotlib만 사용."""
from __future__ import annotations

import numpy as np
from matplotlib import patheffects as pe
from matplotlib.patches import Circle, Rectangle

PLANES = {"xy": (0, 1), "xz": (0, 2), "yz": (1, 2)}
_STRUCT = "#52514e"
_PIPE = "#898781"
_HALO = [pe.withStroke(linewidth=2.6, foreground="#fcfcfb")]
_LABELS = {"spent_bed": "Bed A", "bed_B": "Bed B", "cask_seat": "cask", "rack_seat": "rack (new bed)"}


def _bed_object(center, bed: dict, oid: str) -> dict:
    return {"id": oid, "kind": "cylinder", "center": list(center), "radius": bed["radius"],
            "height": bed["height"], "role": "bed"}


def objects_for_state(layout: dict, state: str = "pre_removal") -> list[dict]:
    """state: pre_removal | post_removal | installed. 이동 물체(베드) 위치를 반영한 목록."""
    objs = [o for o in layout["objects"] if o["id"] not in ("floor",) and not o["id"].startswith("wall")]
    bed = layout["bed_cartridge"]
    sites = layout["task_sites"]
    if state == "pre_removal":
        objs.append(_bed_object(layout["movable"]["spent_bed"]["initial_center"], bed, "spent_bed"))
        objs.append(_bed_object(layout["movable"]["new_bed"]["initial_center"], bed, "new_bed"))
    elif state == "post_removal":
        objs.append(_bed_object(sites["cask_place_center"], bed, "spent_bed(cask)"))
        objs.append(_bed_object(layout["movable"]["new_bed"]["initial_center"], bed, "new_bed"))
    elif state == "installed":
        objs.append(_bed_object(sites["cask_place_center"], bed, "spent_bed(cask)"))
        objs.append(_bed_object(sites["bed_A_center"], bed, "new_bed"))
    return objs


def draw_layout(ax, layout: dict, plane: str = "xy", state: str = "pre_removal",
                labels: bool = True, color: str = _STRUCT, lw: float = 0.9, robot: bool = True,
                zorder: int = 5) -> None:
    a, b = PLANES[plane]
    lo = np.asarray(layout["cell"]["interior_min"])
    hi = np.asarray(layout["cell"]["interior_max"])
    ax.add_patch(Rectangle((lo[a], lo[b]), hi[a] - lo[a], hi[b] - lo[b], fill=False,
                           ec=color, lw=lw * 1.4, zorder=zorder))
    for o in objects_for_state(layout, state):
        k = o["kind"]
        c = np.asarray(o.get("center", [0, 0, 0]), float)
        if k == "box":
            h = np.asarray(o["half_extents"])
            ax.add_patch(Rectangle((c[a] - h[a], c[b] - h[b]), 2 * h[a], 2 * h[b], fill=False,
                                   ec=color, lw=lw, zorder=zorder, path_effects=_HALO))
        elif k == "cylinder":
            r, hgt = o["radius"], o["height"]
            if plane == "xy":
                ax.add_patch(Circle((c[0], c[1]), r, fill=False, ec=color, lw=lw, zorder=zorder,
                                    path_effects=_HALO))
            else:
                ax.add_patch(Rectangle((c[a] - r, c[2] - hgt / 2), 2 * r, hgt, fill=False,
                                       ec=color, lw=lw, zorder=zorder, path_effects=_HALO))
        elif k == "capsule_segment":
            s, e = np.asarray(o["start"]), np.asarray(o["end"])
            ax.plot([s[a], e[a]], [s[b], e[b]], color=_PIPE, lw=2.2, solid_capstyle="round",
                    zorder=zorder)
            continue
        if labels and o["id"] in _LABELS and not (plane != "xy" and o["id"] in ("cask_seat", "rack_seat")):
            if plane == "xy":
                ty = c[1] + o.get("radius", 0.1) + 0.03
            else:
                ty = c[2] + o.get("height", 0.1) / 2 + 0.03
            ax.text(c[a], ty, _LABELS[o["id"]], ha="center", va="bottom", fontsize=7, color=color,
                    zorder=zorder + 1, path_effects=_HALO)
    if robot:
        base = np.asarray(layout["robot"]["base_position"])
        if plane == "xy":
            ax.add_patch(Circle((base[0], base[1]), 0.11, fill=False, ec=color, lw=lw, ls="--", zorder=zorder,
                                path_effects=_HALO))
            ax.text(base[0], base[1] - 0.14, "robot", ha="center", va="top", fontsize=7, color=color,
                    path_effects=_HALO)
        else:
            ax.add_patch(Rectangle((base[a] - 0.11, 0.0), 0.22, 0.36, fill=False, ec=color, lw=lw,
                                   ls="--", zorder=zorder, path_effects=_HALO))
    ax.set_xlim(lo[a] - 0.05, hi[a] + 0.05)
    ax.set_ylim(lo[b] - 0.05, hi[b] + 0.05)
    ax.set_aspect("equal")
    names = "xyz"
    ax.set_xlabel(f"{names[a]} [m]")
    ax.set_ylabel(f"{names[b]} [m]")


def source_points(meta_sources: list[dict]) -> list[np.ndarray]:
    out = []
    for s in meta_sources:
        if "position" in s:
            out.append(np.atleast_2d(s["position"]))
        elif "start" in s:
            out.append(np.asarray([s["start"], s["end"]]))
        elif "points" in s:
            out.append(np.asarray(s["points"]))
    return out


def draw_sources(ax, meta_sources: list[dict], plane: str = "xy", color: str = "#e34948") -> None:
    a, b = PLANES[plane]
    for pts in source_points(meta_sources):
        if len(pts) == 1:
            ax.plot(pts[0, a], pts[0, b], marker="x", ms=6, mew=1.6, color=color, zorder=8)
        else:
            ax.plot(pts[:, a], pts[:, b], color=color, lw=1.4, ls=(0, (2, 1.5)), zorder=8)
