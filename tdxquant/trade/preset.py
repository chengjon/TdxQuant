from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

TRADE_COMMAND_DEFAULT_PROFILES: dict[str, str] = {
    "broker-capabilities": "balanced",
    "buy": "balanced",
    "submit-once": "submit_once",
}


def get_trade_preset_path() -> Path:
    return Path(__file__).resolve().parents[2] / "runtime" / "trade-presets.json"


def load_trade_presets(path: Path | None = None) -> dict[str, dict[str, Any]]:
    preset_path = path or get_trade_preset_path()
    payload = json.loads(preset_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("trade preset file must contain a JSON object")
    presets: dict[str, dict[str, Any]] = {}
    for name, value in payload.items():
        if not isinstance(name, str) or not isinstance(value, dict):
            raise ValueError("trade preset entries must map preset names to JSON objects")
        presets[name] = value
    return presets


def resolve_trade_preset(
    preset_name: str,
    overrides: dict[str, Any] | None = None,
    *,
    path: Path | None = None,
    presets: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    available = presets if presets is not None else load_trade_presets(path)
    try:
        raw_preset = available[preset_name]
    except KeyError as exc:
        raise ValueError(f"unsupported trade preset: {preset_name}") from exc

    resolved = _normalize_trade_preset(preset_name, raw_preset)
    override_payload = copy.deepcopy(overrides or {})
    option_overrides = override_payload.pop("options", None)
    for key, value in override_payload.items():
        if value is not None:
            resolved[key] = value
    if option_overrides is not None:
        if not isinstance(option_overrides, dict):
            raise ValueError("trade preset option overrides must be a JSON object")
        for key, value in option_overrides.items():
            if value is not None:
                resolved["options"][key] = copy.deepcopy(value)
    return resolved


def _normalize_trade_preset(name: str, value: dict[str, Any]) -> dict[str, Any]:
    raw_command = value.get("command")
    if not isinstance(raw_command, str) or not raw_command:
        raise ValueError(f"trade preset '{name}' must define a non-empty command")
    command = raw_command.strip()

    raw_options = value.get("options", {})
    if raw_options is None:
        raw_options = {}
    if not isinstance(raw_options, dict):
        raise ValueError(f"trade preset '{name}' options must be a JSON object")

    description = value.get("description")
    if description is not None and not isinstance(description, str):
        raise ValueError(f"trade preset '{name}' description must be a string")

    profile = value.get("profile")
    if profile is not None and not isinstance(profile, str):
        raise ValueError(f"trade preset '{name}' profile must be a string")

    title_key = value.get("title_key")
    if title_key is not None and not isinstance(title_key, str):
        raise ValueError(f"trade preset '{name}' title_key must be a string")

    exe_path = value.get("exe_path")
    if exe_path is not None and not isinstance(exe_path, str):
        raise ValueError(f"trade preset '{name}' exe_path must be a string")

    resolved_profile = profile or TRADE_COMMAND_DEFAULT_PROFILES.get(command)
    return {
        "command": command,
        "description": description or "",
        "profile": resolved_profile,
        "title_key": title_key,
        "exe_path": exe_path,
        "options": copy.deepcopy(raw_options),
    }
