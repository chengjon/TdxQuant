from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

REPORT_COMMAND_DEFAULT_PROFILES: dict[str, str] = {
    "ledger": "ledger_summary",
    "daily": "daily_trade_report",
    "lookup": "trade_report_lookup",
    "audit-lookup": "trade_audit_lookup",
    "audit-daily": "trade_audit_daily_report",
    "audit-period": "trade_audit_period_report",
    "period": "trade_period_report",
}


def get_report_preset_path() -> Path:
    return Path(__file__).resolve().parents[1] / "runtime" / "report-presets.json"


def load_report_presets(path: Path | None = None) -> dict[str, dict[str, Any]]:
    preset_path = path or get_report_preset_path()
    payload = json.loads(preset_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("report preset file must contain a JSON object")
    presets: dict[str, dict[str, Any]] = {}
    for name, value in payload.items():
        if not isinstance(name, str) or not isinstance(value, dict):
            raise ValueError("report preset entries must map preset names to JSON objects")
        presets[name] = value
    return presets


def resolve_report_preset(
    preset_name: str,
    overrides: dict[str, Any] | None = None,
    *,
    path: Path | None = None,
    presets: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    available = presets if presets is not None else load_report_presets(path)
    try:
        raw_preset = available[preset_name]
    except KeyError as exc:
        raise ValueError(f"unsupported report preset: {preset_name}") from exc

    resolved = _normalize_report_preset(preset_name, raw_preset)
    override_payload = copy.deepcopy(overrides or {})
    option_overrides = override_payload.pop("options", None)
    for key, value in override_payload.items():
        if value is not None:
            resolved[key] = value
    if option_overrides is not None:
        if not isinstance(option_overrides, dict):
            raise ValueError("report preset option overrides must be a JSON object")
        for key, value in option_overrides.items():
            if value is not None:
                resolved["options"][key] = copy.deepcopy(value)
    return resolved


def _normalize_report_preset(name: str, value: dict[str, Any]) -> dict[str, Any]:
    raw_command = value.get("command")
    if not isinstance(raw_command, str) or not raw_command:
        raise ValueError(f"report preset '{name}' must define a non-empty command")
    command = raw_command.strip()

    raw_options = value.get("options", {})
    if raw_options is None:
        raw_options = {}
    if not isinstance(raw_options, dict):
        raise ValueError(f"report preset '{name}' options must be a JSON object")

    description = value.get("description")
    if description is not None and not isinstance(description, str):
        raise ValueError(f"report preset '{name}' description must be a string")

    profile = value.get("profile")
    if profile is not None and not isinstance(profile, str):
        raise ValueError(f"report preset '{name}' profile must be a string")

    api_profile = value.get("api_profile")
    if api_profile is not None and not isinstance(api_profile, str):
        raise ValueError(f"report preset '{name}' api_profile must be a string")

    strategy_path = value.get("strategy_path")
    if strategy_path is not None and not isinstance(strategy_path, str):
        raise ValueError(f"report preset '{name}' strategy_path must be a string")

    resolved_profile = profile or REPORT_COMMAND_DEFAULT_PROFILES.get(command)
    return {
        "command": command,
        "description": description or "",
        "profile": resolved_profile,
        "api_profile": api_profile,
        "strategy_path": strategy_path,
        "options": copy.deepcopy(raw_options),
    }
