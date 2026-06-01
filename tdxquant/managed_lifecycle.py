from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any

MANAGED_LIFECYCLE_MODULE = "tdxquant.managed_lifecycle"
MANAGED_LIFECYCLE_PROVENANCE_SCHEMA_VERSION = "tdx.managed_process_lifecycle.provenance.v1"
PROCESS_LIVENESS_SCHEMA_VERSION = "tdx.managed_process_lifecycle.process_liveness.v1"
PROCESS_OWNERSHIP_SCHEMA_VERSION = "tdx.managed_process_lifecycle.process_ownership.v1"
RESTART_BACKOFF_PROJECTION_SCHEMA_VERSION = (
    "tdx.managed_process_lifecycle.restart_backoff_projection.v1"
)
PROCESS_LIVENESS_BOUNDARY = "read_only_process_liveness_probe; no_process_control"
PROCESS_OWNERSHIP_BOUNDARY = "read_only_process_ownership_diagnostics; no_process_control"
MANAGED_LIFECYCLE_PROVENANCE_BOUNDARY = "diagnostic_provenance_only; no_lifecycle_control"


def coerce_process_pid(raw_pid: Any) -> int:
    try:
        pid = int(raw_pid or 0)
    except (TypeError, ValueError):
        return 0
    return pid if pid > 0 else 0


def process_pid_alive(pid: int) -> bool:
    resolved_pid = coerce_process_pid(pid)
    if resolved_pid < 1:
        return False
    try:
        os.kill(resolved_pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def build_process_liveness(
    raw_pid: Any,
    *,
    pid_is_alive: Any | None = None,
) -> dict[str, Any]:
    pid = coerce_process_pid(raw_pid)
    if pid < 1:
        return {
            "schema_version": PROCESS_LIVENESS_SCHEMA_VERSION,
            "pid": None,
            "pid_valid": False,
            "pid_live": False,
            "boundary": PROCESS_LIVENESS_BOUNDARY,
        }
    probe = pid_is_alive or process_pid_alive
    return {
        "schema_version": PROCESS_LIVENESS_SCHEMA_VERSION,
        "pid": pid,
        "pid_valid": True,
        "pid_live": bool(probe(pid)),
        "boundary": PROCESS_LIVENESS_BOUNDARY,
    }


def build_managed_lifecycle_provenance(
    *,
    adapter: str,
    primitives: list[str] | tuple[str, ...],
) -> dict[str, Any]:
    return {
        "schema_version": MANAGED_LIFECYCLE_PROVENANCE_SCHEMA_VERSION,
        "module": MANAGED_LIFECYCLE_MODULE,
        "adapter": adapter,
        "primitives": list(primitives),
        "boundary": MANAGED_LIFECYCLE_PROVENANCE_BOUNDARY,
    }


def build_process_ownership_diagnostics(
    statefile_check: dict[str, Any] | None,
    *,
    expected_owner_token: str | None = None,
    process_running: Any | None = None,
    expected_command: list[str] | None = None,
    process_identity_matches: Any | None = None,
    adapter: str = "managed_process_lifecycle",
) -> dict[str, Any]:
    pid = statefile_check.get("pid") if isinstance(statefile_check, dict) else None
    owner_token = statefile_check.get("owner_token") if isinstance(statefile_check, dict) else None
    owner_token_present = isinstance(owner_token, str) and bool(owner_token)
    expected_owner_token_present = isinstance(expected_owner_token, str) and bool(expected_owner_token)
    owner_token_matches = None
    if expected_owner_token_present:
        owner_token_matches = owner_token == expected_owner_token

    diagnostics: dict[str, Any] = {
        "schema_version": PROCESS_OWNERSHIP_SCHEMA_VERSION,
        "ownership_status": "unknown_process_identity",
        "owned_process": False,
        "pid": pid if isinstance(pid, int) else None,
        "pid_live": None,
        "owner_token_present": owner_token_present,
        "owner_token_matches": owner_token_matches,
        "config_hash_matches": statefile_check.get("config_hash_matches")
        if isinstance(statefile_check, dict)
        else None,
        "process_identity_checked": False,
        "process_identity_matches": None,
        "control_allowed": False,
        "managed_lifecycle": build_managed_lifecycle_provenance(
            adapter=adapter,
            primitives=["process_liveness", "process_ownership"],
        ),
        "boundary": PROCESS_OWNERSHIP_BOUNDARY,
    }

    if not isinstance(statefile_check, dict):
        diagnostics["ownership_status"] = "invalid_statefile"
        return diagnostics
    if statefile_check.get("configured") is not True:
        diagnostics["ownership_status"] = "not_configured"
        return diagnostics
    if statefile_check.get("check_status") == "missing":
        diagnostics["ownership_status"] = "missing_statefile"
        return diagnostics
    if statefile_check.get("check_status") != "valid":
        diagnostics["ownership_status"] = "invalid_statefile"
        return diagnostics
    if statefile_check.get("stale") is True:
        diagnostics["ownership_status"] = "stale_statefile"
        return diagnostics
    if statefile_check.get("config_hash_matches") is not True:
        diagnostics["ownership_status"] = "config_hash_mismatch"
        return diagnostics
    if expected_owner_token_present and owner_token_matches is not True:
        diagnostics["ownership_status"] = "owner_token_mismatch"
        return diagnostics
    if not isinstance(pid, int):
        diagnostics["ownership_status"] = "invalid_statefile"
        return diagnostics

    if callable(process_running):
        try:
            diagnostics["pid_live"] = bool(process_running(pid))
        except OSError:
            diagnostics["pid_live"] = None
    if diagnostics["pid_live"] is False:
        diagnostics["ownership_status"] = "process_not_running"
        return diagnostics
    if diagnostics["pid_live"] is not True:
        diagnostics["ownership_status"] = "unknown_process_identity"
        return diagnostics

    if callable(process_identity_matches):
        diagnostics["process_identity_checked"] = True
        command = expected_command or []
        try:
            identity_matches = process_identity_matches(pid, command)
        except OSError:
            identity_matches = None
        if identity_matches is True:
            diagnostics["process_identity_matches"] = True
        elif identity_matches is False:
            diagnostics["process_identity_matches"] = False
            diagnostics["ownership_status"] = "process_identity_mismatch"
            return diagnostics
        else:
            diagnostics["process_identity_matches"] = None
            diagnostics["ownership_status"] = "unknown_process_identity"
            return diagnostics

    diagnostics["ownership_status"] = "owned"
    diagnostics["owned_process"] = True
    diagnostics["control_allowed"] = True
    return diagnostics


def build_restart_backoff_projection(
    *,
    reason: str,
    created_at: datetime,
    backoff_seconds: float | int,
    boundary: str,
) -> dict[str, Any]:
    resolved_backoff_seconds = max(float(backoff_seconds), 0.0)
    retry_after_at = created_at + timedelta(seconds=resolved_backoff_seconds)
    return {
        "schema_version": RESTART_BACKOFF_PROJECTION_SCHEMA_VERSION,
        "status": "active",
        "reason_codes": ["BACKOFF_ACTIVE"],
        "reason": reason,
        "created_at": created_at.isoformat(),
        "retry_after_at": retry_after_at.isoformat(),
        "backoff_seconds": resolved_backoff_seconds,
        "boundary": boundary,
    }
