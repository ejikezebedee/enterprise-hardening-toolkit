from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.core.config import BASELINES_DIR


def load_baseline(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        if path.suffix.lower() in {".yaml", ".yml"}:
            return yaml.safe_load(handle) or {}
        raise ValueError(f"Unsupported baseline format: {path.suffix}")


def load_all_baselines(directory: Path = BASELINES_DIR) -> list[dict[str, Any]]:
    baselines = []
    for path in sorted(directory.glob("*.yaml")):
        data = load_baseline(path)
        data["_source_path"] = str(path)
        baselines.append(data)
    return baselines


def build_control_index(directory: Path = BASELINES_DIR) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for baseline in load_all_baselines(directory):
        for control in baseline.get("controls", []):
            index[control["check_id"]] = control
    return index

