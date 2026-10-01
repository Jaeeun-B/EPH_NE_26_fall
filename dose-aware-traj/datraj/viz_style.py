"""그림 공통 스타일 (matplotlib). 색은 단일 팔레트에서 역할별로 가져다 쓴다."""
from __future__ import annotations

import warnings

import matplotlib

matplotlib.use("Agg") if matplotlib.get_backend().lower() not in ("macosx", "tkagg", "qtagg") else None
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

# 범주형: 고정 순서 (순환 금지)
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
STAGE_COLORS = {f"S{i + 1}": c for i, c in enumerate(CATEGORICAL[:6])}

# 순차형: 파랑 한 가지 (선량률 크기)
SEQ_BLUE = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
            "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
DOSE_CMAP = LinearSegmentedColormap.from_list("dose_blue", SEQ_BLUE)

# 배치도 외곽선
OUTLINE = "#52514e"
SOURCE_MARK = "#e34948"

_KO_FONTS = ["Apple SD Gothic Neo", "AppleGothic", "Noto Sans CJK KR", "Noto Sans CJK JP",
             "NanumGothic", "Malgun Gothic", "DejaVu Sans"]


def apply() -> None:
    available = {f.name for f in font_manager.fontManager.ttflist}
    family = [f for f in _KO_FONTS if f in available] or ["DejaVu Sans"]
    plt.rcParams.update({
        "font.family": family,
        "axes.unicode_minus": False,
        "mathtext.fontset": "dejavusans",
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": AXIS,
        "axes.labelcolor": INK_2,
        "axes.titlecolor": INK,
        "axes.titlesize": 11,
        "axes.labelsize": 9,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "axes.grid": False,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "legend.fontsize": 8,
        "lines.linewidth": 2.0,
        "figure.dpi": 110,
        "savefig.dpi": 160,
        "savefig.bbox": "tight",
    })
    warnings.filterwarnings("ignore", message=".*Glyph.*missing.*")
