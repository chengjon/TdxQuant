from __future__ import annotations

import copy
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, TypeVar

from ..models import Result
from ..result_contract import DEFAULT_CAPABILITY_VERSION, DEFAULT_SCHEMA_VERSION, build_runtime_metadata, format_rfc3339, utc_now

T = TypeVar("T")


def get_api_profile_path() -> Path:
    return Path(__file__).resolve().parents[2] / "runtime" / "api-profiles.json"


def load_api_profiles(path: Path | None = None) -> dict[str, dict[str, Any]]:
    profile_path = path or get_api_profile_path()
    payload = json.loads(profile_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("api profile file must contain a JSON object")
    profiles: dict[str, dict[str, Any]] = {}
    for name, value in payload.items():
        if not isinstance(name, str) or not isinstance(value, dict):
            raise ValueError("api profile entries must map profile names to JSON objects")
        profiles[name] = value
    return profiles


def resolve_api_profile(
    profile_name: str,
    overrides: dict[str, Any] | None = None,
    *,
    path: Path | None = None,
    profiles: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    available = profiles if profiles is not None else load_api_profiles(path)
    try:
        resolved = copy.deepcopy(available[profile_name])
    except KeyError as exc:
        raise ValueError(f"unsupported api profile: {profile_name}") from exc
    for key, value in (overrides or {}).items():
        if value is not None:
            resolved[key] = copy.deepcopy(value)
    return resolved


def capture_api_timing(step_name: str, fn: Callable[[], T]) -> tuple[T, dict[str, Any]]:
    started_wall = utc_now()
    started_at = time.perf_counter()
    value = fn()
    finished_wall = utc_now()
    total_ms = round((time.perf_counter() - started_at) * 1000, 3)
    return value, {
        "manager_call": {
            "name": step_name,
            "total_ms": total_ms,
            "started_at": format_rfc3339(started_wall),
            "finished_at": format_rfc3339(finished_wall),
        }
    }


def build_manager_call_metadata(
    *,
    profile_name: str,
    profile_options: dict[str, Any],
    domain: str,
    method: str,
    timing: dict[str, Any],
) -> dict[str, Any]:
    return {
        "manager": {
            "entrypoint": "TdxApiManager",
            "domain": domain,
            "method": method,
        },
        "api_profile": {
            "name": profile_name,
            "options": copy.deepcopy(profile_options),
        },
        "timing": timing,
    }


def attach_manager_metadata(
    result: Result,
    *,
    profile_name: str,
    profile_options: dict[str, Any],
    domain: str,
    method: str,
    timing: dict[str, Any],
) -> Result:
    metadata = build_manager_call_metadata(
        profile_name=profile_name,
        profile_options=profile_options,
        domain=domain,
        method=method,
        timing=timing,
    )
    result.data["manager"] = metadata["manager"]
    result.data["api_profile"] = metadata["api_profile"]
    result.data.setdefault("timing", {}).update(metadata["timing"])
    manager_timing = timing.get("manager_call", {})
    existing_contract = dict(result._provider_contract or {})
    result._provider_contract = {
        "capability": existing_contract.get("capability") or f"{domain}.{method}",
        "capability_version": existing_contract.get("capability_version") or DEFAULT_CAPABILITY_VERSION,
        "schema_version": existing_contract.get("schema_version") or DEFAULT_SCHEMA_VERSION,
        "request_id": existing_contract.get("request_id"),
        "started_at": manager_timing.get("started_at"),
        "finished_at": manager_timing.get("finished_at"),
        "elapsed_ms": manager_timing.get("total_ms"),
        "runtime": existing_contract.get("runtime") or build_runtime_metadata(mode="manager"),
        "warnings": list(existing_contract.get("warnings") or result.warnings),
        "artifacts": list(existing_contract.get("artifacts") or result._provider_artifacts or []),
    }
    return result
