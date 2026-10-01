"""결과 그림 (matplotlib)과 PyBullet GUI 재생."""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np

from . import config, viz_style
from .layout_plot import draw_layout
from .task import STAGE_NAMES, STAGES, apply_state


def _plane_rates(field, plane="xy", at=0.55, n=140, layout=None):
    layout = layout or config.layout()
    lo = np.asarray(layout["cell"]["interior_min"], float)
    hi = np.asarray(layout["cell"]["interior_max"], float)
    a, b = {"xy": (0, 1), "xz": (0, 2)}[plane]
    A = np.linspace(lo[a], hi[a], n)
    B = np.linspace(lo[b], min(hi[b], 1.5), n)
    AA, BB = np.meshgrid(A, B, indexing="ij")
    P = np.zeros(AA.shape + (3,))
    P[..., a], P[..., b] = AA, BB
    P[..., 3 - a - b] = at
    flat = P.reshape(1, -1, 3)
    vals = field.rate(flat, np.zeros((1, 3)), np.eye(3)[None], np.zeros(1)).reshape(AA.shape)
    return A, B, vals


def trajectory_figures(E, segs, comps, scene, fields, out: Path, tag: str) -> None:
    viz_style.apply()
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm

    out = Path(out)
    layout = scene.layout
    tcp = np.array([scene.robot.tcp_pose(q)[0] for q in E.q[::5]])
    stg = np.array(E.stage[::5])

    # 1) 경로와 선량장 (위, 옆)
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.6), gridspec_kw={"width_ratios": [1, 1.05]})
    for ax, plane, at in ((axs[0], "xy", 0.55), (axs[1], "xz", -0.28)):
        A, B, V = _plane_rates(fields["pre"], plane, at, layout=layout)
        vmax = np.percentile(V, 99.5)
        ax.pcolormesh(A, B, np.clip(V.T, vmax * 1e-3, None), cmap=viz_style.DOSE_CMAP,
                      norm=LogNorm(vmin=vmax * 1e-3, vmax=vmax), shading="auto", alpha=0.85, zorder=1)
        draw_layout(ax, layout, plane, state="pre_removal")
        a, b = (0, 1) if plane == "xy" else (0, 2)
        for s in STAGES:
            m = stg == s
            if m.any():
                ax.plot(tcp[m, a], tcp[m, b], ".", ms=2.2, color=viz_style.STAGE_COLORS[s], zorder=7,
                        label=f"{s} {STAGE_NAMES[s]}")
        if plane == "xz":
            ax.set_ylim(top=max(1.3, float(tcp[:, 2].max()) + 0.08))
    axs[0].set_title("TCP 경로 (위에서, 배경: 베드 제거 전 선량률 z = 0.55 m)", loc="left", fontsize=10)
    axs[1].set_title("TCP 경로 (옆에서, 배경: y = -0.28 m 단면)", loc="left", fontsize=10)
    h, lab = axs[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=len(lab), markerscale=5, fontsize=8, frameon=False,
               bbox_to_anchor=(0.5, -0.04))
    fig.savefig(out / f"path_{tag}.png")
    plt.close(fig)

    # 2) 부품별 단계 선량 (누적 막대)
    real = [k for k, c in enumerate(comps) if not c.reference]
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    left = np.zeros(len(real))
    ylab = [f"{comps[k].id} {comps[k].name}" for k in real]
    for s in STAGES:
        v = np.array([E.dose_stage[s][k] for k in real]) * 1e3
        ax.barh(range(len(real)), v, left=left, color=viz_style.STAGE_COLORS[s], height=0.62,
                edgecolor=viz_style.SURFACE, linewidth=1.0, label=f"{s} {STAGE_NAMES[s]}")
        left += v
    tcp_k = next((k for k, c in enumerate(comps) if c.reference), None)
    if tcp_k is not None:
        ax.axvline(E.dose_total[tcp_k] * 1e3, color=viz_style.INK_2, lw=1, ls="--")
        ax.text(E.dose_total[tcp_k] * 1e3, len(real) - 0.3, " 점 로봇(TCP)", fontsize=8, color=viz_style.INK_2,
                va="bottom")
    for i, v in enumerate(left):
        ax.text(v, i, f" {v:.2f}", va="center", fontsize=7.5, color=viz_style.INK_2)
    ax.set_yticks(range(len(real)), ylab, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("누적선량 [mGy] (가상 선원 기준, 상대 비교용)")
    ax.set_title(f"부품별 누적선량과 단계 구성: {E.summary['label']}", loc="left")
    ax.legend(ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.13), fontsize=7.5)
    ax.grid(True, axis="x")
    ax.set_axisbelow(True)
    fig.savefig(out / f"dose_components_{tag}.png")
    plt.close(fig)

    # 3) 시간축: 선량률과 토크 사용률
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6.2), sharex=True, gridspec_kw={"height_ratios": [1.4, 1]})
    kmax = real[int(np.argmax(E.dose_total[real]))]
    base_k = next((k for k, c in enumerate(comps) if c.group == "base"), real[0])
    show = [(kmax, comps[kmax].name, viz_style.CATEGORICAL[0])]
    if tcp_k is not None:
        show.append((tcp_k, "TCP (점 로봇)", viz_style.CATEGORICAL[1]))
    if base_k != kmax:
        show.append((base_k, comps[base_k].name, viz_style.CATEGORICAL[2]))
    bounds = []
    for s in STAGES:
        ss = [sg for sg in segs if sg.step.stage == s]
        if ss:
            bounds.append((s, ss[0].traj.t[0], ss[-1].traj.t[-1]))
    for ax in (a1, a2):
        for j, (s, t0, t1) in enumerate(bounds):
            if j % 2 == 0:
                ax.axvspan(t0, t1, color=viz_style.GRID, alpha=0.45, lw=0)
    for k, name, col in show:
        a1.plot(E.t, np.maximum(E.rates[:, k], 1e-6), color=col, lw=1.4, label=name)
    a1.set_yscale("log")
    a1.set_ylabel("선량률 [Gy/h]")
    a1.legend(loc="upper right", fontsize=8)
    ymax = a1.get_ylim()[1]
    span = E.t[-1] - E.t[0]
    for s, t0, t1 in bounds:
        txt = f"{s}\n{STAGE_NAMES[s]}" if (t1 - t0) > 0.06 * span else s
        a1.text((t0 + t1) / 2, ymax, txt, ha="center", va="bottom", fontsize=7.5, color=viz_style.INK_2)
    m = ~np.isnan(E.util_env)
    a2.plot(E.t[m], E.util_env[m], color=viz_style.CATEGORICAL[6], lw=1.2)
    a2.axhline(E.summary["torque_cap"], color=viz_style.CATEGORICAL[7], lw=1, ls="--")
    a2.text(E.t[0], E.summary["torque_cap"], " 상한 0.8", va="bottom", fontsize=8, color=viz_style.INK_2)
    a2.set_ylabel("최대 토크 사용률\n(경사 포락선)")
    a2.set_xlabel("시간 [s]")
    a2.set_ylim(0, max(1.0, np.nanmax(E.util_env) * 1.1))
    fig.savefig(out / f"timeline_{tag}.png")
    plt.close(fig)


def replay_gui(E, segs, fields, speed: float = 1.0, fps: float = 30.0) -> None:
    """PyBullet 창에서 궤적 재생. TCP 궤적을 선량률(부품 중 최댓값) 색으로 남긴다.

    체류 구간은 1초 동안 안내 문구만 띄우고 건너뛴다. 창을 닫거나 Ctrl+C로 종료.
    """
    import pybullet as p
    from matplotlib.colors import LogNorm

    from .scene import Scene

    sc = Scene(gui=True)
    rates = E.rates.max(axis=1)
    norm = LogNorm(vmin=max(rates.min(), rates.max() * 1e-3), vmax=rates.max())
    frame = 1.0 / fps
    prev, cur_seg, k = None, -1, 0
    print("재생 중... (창을 닫으면 종료)")
    try:
        while k < len(E.t) and p.isConnected(sc.cid):
            si = int(E.seg_index[k])
            st = segs[si].step
            if si != cur_seg:
                apply_state(sc, st.state)
                cur_seg = si
            sc.robot.set_q(E.q[k])
            sc.update_attached(E.q[k])
            tcp, _ = sc.robot.tcp_pose(E.q[k])
            if prev is None:
                prev = tcp
            elif np.linalg.norm(tcp - prev) > 0.01:
                col = viz_style.DOSE_CMAP(norm(max(rates[k], norm.vmin)))[:3]
                p.addUserDebugLine(prev.tolist(), tcp.tolist(), col, 3, physicsClientId=sc.cid)
                prev = tcp
            if st.kind == "dwell":
                p.addUserDebugText(f"{st.stage} {st.name}: {segs[si].traj.duration:.0f} s 체류",
                                   (tcp + [0, 0, 0.15]).tolist(), [0.1, 0.1, 0.1], 1.3, lifeTime=1.2,
                                   physicsClientId=sc.cid)
                time.sleep(1.2)
                nxt = np.nonzero(E.seg_index > si)[0]
                k = int(nxt[0]) if len(nxt) else len(E.t)
                continue
            time.sleep(frame)
            k = max(k + 1, int(np.searchsorted(E.t, E.t[k] + frame * speed)))
        print("재생 끝. 창을 닫으면 종료합니다.")
        while p.isConnected(sc.cid):
            time.sleep(0.1)
    except (KeyboardInterrupt, p.error):
        pass  # Ctrl+C 또는 재생 중 창을 닫은 경우
