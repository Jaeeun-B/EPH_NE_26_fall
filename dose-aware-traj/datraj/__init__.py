"""Dose-aware trajectory optimization (E 파트) 공용 모듈."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
DATA = ROOT / "data"
GRID_DIR = DATA / "dose_grids"
OUTPUTS = ROOT / "outputs"

__all__ = ["ROOT", "CONFIG", "DATA", "GRID_DIR", "OUTPUTS"]
