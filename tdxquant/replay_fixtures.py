from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


def get_provider_replay_fixture_dir() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "provider"


_PROVIDER_REPLAY_FIXTURE_REGISTRY: list[dict[str, str]] = [
    {
        "name": "provider-result-success",
        "capability": "provider.result",
        "format": "json",
        "description": "Minimal successful synchronous provider result envelope sample.",
        "relative_path": "provider-result-success.json",
    },
    {
        "name": "provider-result-failure",
        "capability": "provider.result",
        "format": "json",
        "description": "Minimal failed synchronous provider result envelope sample.",
        "relative_path": "provider-result-failure.json",
    },
    {
        "name": "formula-screen-success",
        "capability": "formula.screen",
        "format": "json",
        "description": "Representative successful formula.screen provider response sample.",
        "relative_path": "formula-screen-success.json",
    },
    {
        "name": "formula-screen-failure",
        "capability": "formula.screen",
        "format": "json",
        "description": "Representative failed formula.screen provider response sample.",
        "relative_path": "formula-screen-failure.json",
    },
    {
        "name": "runtime-capabilities-success",
        "capability": "runtime.capabilities",
        "format": "json",
        "description": "Representative runtime.capabilities provider response sample.",
        "relative_path": "runtime-capabilities-success.json",
    },
    {
        "name": "runtime-health-degraded",
        "capability": "runtime.health",
        "format": "json",
        "description": "Representative degraded runtime.health provider response sample.",
        "relative_path": "runtime-health-degraded.json",
    },
    {
        "name": "runtime-doctor-degraded",
        "capability": "runtime.doctor",
        "format": "json",
        "description": "Representative degraded runtime.doctor provider response sample.",
        "relative_path": "runtime-doctor-degraded.json",
    },
    {
        "name": "block-send-user-block-applied",
        "capability": "block.send_user_block",
        "format": "json",
        "description": "Representative successful block mutation provider response sample.",
        "relative_path": "block-send-user-block-applied.json",
    },
    {
        "name": "subscription-event-batch",
        "capability": "subscription.quote_update",
        "format": "jsonl",
        "description": "Representative normalized subscription event row batch sample.",
        "relative_path": "subscription-event-batch.jsonl",
    },
    {
        "name": "subscription-watch-events",
        "capability": "subscription.watch",
        "format": "jsonl",
        "description": "Representative canonical subscription-watch event stream sample.",
        "relative_path": "subscription-watch-events.jsonl",
    },
    {
        "name": "subscription-watch-status-completed",
        "capability": "subscription.watch",
        "format": "json",
        "description": "Representative completed subscription-watch status snapshot.",
        "relative_path": "subscription-watch-status-completed.json",
    },
    {
        "name": "subscription-watch-summary-completed",
        "capability": "subscription.watch",
        "format": "json",
        "description": "Representative completed subscription-watch final summary.",
        "relative_path": "subscription-watch-summary-completed.json",
    },
    {
        "name": "subscription-watch-manifest",
        "capability": "subscription.watch",
        "format": "json",
        "description": "Representative subscription-watch run manifest.",
        "relative_path": "subscription-watch-manifest.json",
    },
]


def list_provider_replay_fixtures() -> list[dict[str, str]]:
    return [copy.deepcopy(item) for item in _PROVIDER_REPLAY_FIXTURE_REGISTRY]


def _find_provider_replay_fixture_descriptor(name: str) -> dict[str, str]:
    for item in _PROVIDER_REPLAY_FIXTURE_REGISTRY:
        if item["name"] == name:
            return item
    raise ValueError(f"unsupported provider replay fixture: {name}")
def get_provider_replay_fixture_path(name: str) -> Path:
    descriptor = _find_provider_replay_fixture_descriptor(name)
    return get_provider_replay_fixture_dir() / descriptor["relative_path"]


def load_provider_replay_fixture(name: str) -> Any:
    descriptor = _find_provider_replay_fixture_descriptor(name)
    path = get_provider_replay_fixture_path(name)
    raw_text = path.read_text(encoding="utf-8")
    if descriptor["format"] == "json":
        return json.loads(raw_text)
    if descriptor["format"] == "jsonl":
        rows: list[dict[str, Any]] = []
        for raw_line in raw_text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if isinstance(payload, dict):
                rows.append(payload)
        return rows
    raise ValueError(f"unsupported provider replay fixture format: {descriptor['format']}")
