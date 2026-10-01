"""설정 파일 로더."""
from __future__ import annotations

import json
from pathlib import Path

from . import CONFIG


def load_json(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def layout(path: str | Path | None = None) -> dict:
    return load_json(path or CONFIG / "hotcell_layout.json")


def shared_params(path: str | Path | None = None) -> dict:
    return load_json(path or CONFIG / "shared_params.json")


def virtual_sources(path: str | Path | None = None) -> dict:
    return load_json(path or CONFIG / "virtual_sources.json")


def task_config(path: str | Path | None = None) -> dict:
    return load_json(path or CONFIG / "task.json")


def components_config(path: str | Path | None = None) -> dict:
    return load_json(path or CONFIG / "components.json")
