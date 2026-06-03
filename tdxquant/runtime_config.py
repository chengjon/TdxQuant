from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RuntimeConfigError(ValueError):
    pass


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = PROJECT_ROOT / "runtime"

_RUNTIME_CONFIG_FILES = {
    "api_profiles": "api-profiles.json",
    "task_profiles": "task-profiles.json",
    "task_presets": "task-presets.json",
    "trade_profiles": "trade-profiles.json",
    "trade_presets": "trade-presets.json",
    "report_presets": "report-presets.json",
    "command_catalog": "command-catalog.json",
    "command_bundles": "command-bundles.json",
}


def list_runtime_config_names() -> list[str]:
    return sorted(_RUNTIME_CONFIG_FILES)


def get_runtime_config_path(name: str) -> Path:
    try:
        filename = _RUNTIME_CONFIG_FILES[name]
    except KeyError as exc:
        raise RuntimeConfigError(f"unsupported runtime config: {name}") from exc
    return RUNTIME_ROOT / filename


def load_runtime_config_object(name: str, *, path: Path | None = None) -> dict[str, Any]:
    config_path = path or get_runtime_config_path(name)
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeConfigError(f"{config_path.name} must contain valid JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeConfigError(f"{config_path.name} must contain a JSON object")
    return payload
