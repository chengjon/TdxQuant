from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from .runtime_config import get_runtime_config_path, load_runtime_config_object

SUPPORTED_COMMAND_CATALOG_SOURCES = frozenset({"report", "task", "trade"})


def get_command_catalog_path() -> Path:
    return get_runtime_config_path("command_catalog")


def get_command_bundle_path() -> Path:
    return get_runtime_config_path("command_bundles")


def load_command_catalog(path: Path | None = None) -> dict[str, dict[str, Any]]:
    payload = load_runtime_config_object("command_catalog", path=path)
    entries: dict[str, dict[str, Any]] = {}
    for name, value in payload.items():
        if not isinstance(name, str) or not isinstance(value, dict):
            raise ValueError("command catalog entries must map entry names to JSON objects")
        entries[name] = value
    return entries


def load_command_bundles(path: Path | None = None) -> dict[str, dict[str, Any]]:
    payload = load_runtime_config_object("command_bundles", path=path)
    bundles: dict[str, dict[str, Any]] = {}
    for name, value in payload.items():
        if not isinstance(name, str) or not isinstance(value, dict):
            raise ValueError("command bundle entries must map bundle names to JSON objects")
        bundles[name] = value
    return bundles


def _normalize_catalog_labels(raw_labels: Any, *, owner_description: str) -> list[str]:
    if raw_labels is None:
        return []
    if not isinstance(raw_labels, list):
        raise ValueError(f"{owner_description} labels must be a JSON array")
    labels: list[str] = []
    for index, label in enumerate(raw_labels, start=1):
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"{owner_description} label {index} must be a non-empty string")
        normalized_label = label.strip()
        if normalized_label not in labels:
            labels.append(normalized_label)
    return labels


def resolve_command_catalog_entry(
    entry_name: str,
    *,
    path: Path | None = None,
    entries: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    available = entries if entries is not None else load_command_catalog(path)
    try:
        raw_entry = available[entry_name]
    except KeyError as exc:
        raise ValueError(f"unsupported command catalog entry: {entry_name}") from exc

    source = raw_entry.get("source")
    if not isinstance(source, str) or not source.strip():
        raise ValueError(f"command catalog entry '{entry_name}' must define a non-empty source")
    normalized_source = source.strip()
    if normalized_source not in SUPPORTED_COMMAND_CATALOG_SOURCES:
        raise ValueError(
            f"command catalog entry '{entry_name}' source must be one of: "
            + ", ".join(sorted(SUPPORTED_COMMAND_CATALOG_SOURCES))
        )

    preset = raw_entry.get("preset")
    if not isinstance(preset, str) or not preset.strip():
        raise ValueError(f"command catalog entry '{entry_name}' must define a non-empty preset")

    description = raw_entry.get("description")
    if description is not None and not isinstance(description, str):
        raise ValueError(f"command catalog entry '{entry_name}' description must be a string")
    labels = _normalize_catalog_labels(raw_entry.get("labels"), owner_description=f"command catalog entry '{entry_name}'")

    return {
        "source": normalized_source,
        "preset": preset.strip(),
        "description": description or "",
        "labels": labels,
    }


def resolve_command_bundle(
    bundle_name: str,
    *,
    path: Path | None = None,
    bundles: dict[str, dict[str, Any]] | None = None,
    entries: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    available_bundles = bundles if bundles is not None else load_command_bundles(path)
    try:
        raw_bundle = available_bundles[bundle_name]
    except KeyError as exc:
        raise ValueError(f"unsupported command bundle: {bundle_name}") from exc

    description = raw_bundle.get("description")
    if description is not None and not isinstance(description, str):
        raise ValueError(f"command bundle '{bundle_name}' description must be a string")
    labels = _normalize_catalog_labels(raw_bundle.get("labels"), owner_description=f"command bundle '{bundle_name}'")

    raw_steps = raw_bundle.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise ValueError(f"command bundle '{bundle_name}' must define a non-empty steps list")

    available_entries = entries if entries is not None else load_command_catalog()
    resolved_steps: list[dict[str, Any]] = []
    seen_step_names: set[str] = set()
    for index, raw_step in enumerate(raw_steps, start=1):
        if not isinstance(raw_step, dict):
            raise ValueError(f"command bundle '{bundle_name}' step {index} must be a JSON object")

        raw_entry_name = raw_step.get("entry")
        if not isinstance(raw_entry_name, str) or not raw_entry_name.strip():
            raise ValueError(f"command bundle '{bundle_name}' step {index} must define a non-empty entry")
        entry_name = raw_entry_name.strip()
        resolved_entry = resolve_command_catalog_entry(entry_name, entries=available_entries)

        step_description = raw_step.get("description")
        if step_description is not None and not isinstance(step_description, str):
            raise ValueError(f"command bundle '{bundle_name}' step {index} description must be a string")

        raw_step_name = raw_step.get("name")
        if raw_step_name is not None and (not isinstance(raw_step_name, str) or not raw_step_name.strip()):
            raise ValueError(f"command bundle '{bundle_name}' step {index} name must be a non-empty string")
        step_name = raw_step_name.strip() if isinstance(raw_step_name, str) else entry_name
        if step_name in seen_step_names:
            raise ValueError(f"command bundle '{bundle_name}' has duplicate step name: {step_name}")
        seen_step_names.add(step_name)

        raw_options = raw_step.get("options", {})
        if raw_options is None:
            raw_options = {}
        if not isinstance(raw_options, dict):
            raise ValueError(f"command bundle '{bundle_name}' step {index} options must be a JSON object")

        resolved_steps.append(
            {
                "index": index,
                "name": step_name,
                "entry": entry_name,
                "source": resolved_entry["source"],
                "preset": resolved_entry["preset"],
                "description": step_description or resolved_entry["description"],
                "options": copy.deepcopy(raw_options),
            }
        )

    return {
        "name": bundle_name,
        "description": description or "",
        "labels": labels,
        "steps": resolved_steps,
    }


def resolve_command_bundle_step_range(
    resolved_bundle: dict[str, Any],
    *,
    only_step: str | None = None,
    from_step: str | None = None,
    to_step: str | None = None,
) -> dict[str, Any]:
    if only_step is not None and (from_step is not None or to_step is not None):
        raise ValueError("only-step cannot be combined with from-step or to-step")

    steps = resolved_bundle.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValueError("resolved command bundle must contain a non-empty steps list")

    def _resolve_step_ref(step_ref: str, *, option_name: str) -> int:
        normalized_ref = step_ref.strip()
        if not normalized_ref:
            raise ValueError(f"{option_name} must be a non-empty string")
        if normalized_ref.isdigit():
            numeric_index = int(normalized_ref)
            if 1 <= numeric_index <= len(steps):
                return numeric_index
        for step in steps:
            if str(step.get("name")) == normalized_ref:
                return int(step["index"])
        raise ValueError(f"unknown bundle step for {option_name}: {normalized_ref}")

    if only_step is not None:
        selected_index = _resolve_step_ref(only_step, option_name="only-step")
        selected_steps = [step for step in steps if int(step["index"]) == selected_index]
    else:
        start_index = 1 if from_step is None else _resolve_step_ref(from_step, option_name="from-step")
        end_index = len(steps) if to_step is None else _resolve_step_ref(to_step, option_name="to-step")
        if start_index > end_index:
            raise ValueError("bundle step range is invalid: resolved from-step is after to-step")
        selected_steps = [step for step in steps if start_index <= int(step["index"]) <= end_index]

    if not selected_steps:
        raise ValueError("bundle step range resolved to an empty selection")

    return {
        "start_index": int(selected_steps[0]["index"]),
        "end_index": int(selected_steps[-1]["index"]),
        "start_name": str(selected_steps[0]["name"]),
        "end_name": str(selected_steps[-1]["name"]),
        "steps": [copy.deepcopy(step) for step in selected_steps],
    }
