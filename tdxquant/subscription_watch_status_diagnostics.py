from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


RESTARTABILITY_BOUNDARY = "read_only;does_not_stop_start_or_schedule_restart"


def build_subscription_watch_status_diagnostics(
    summary_view: dict[str, Any], *, status_payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Build compact diagnostics flags from the existing watch-status summary view."""
    status_summary = summary_view.get("status_summary")
    status_summary = status_summary if isinstance(status_summary, dict) else {}
    governance = summary_view.get("governance")
    governance = governance if isinstance(governance, dict) else {}

    control_rollup = status_summary.get("control_rollup")
    control_rollup = control_rollup if isinstance(control_rollup, dict) else {}
    consistency_rollup = status_summary.get("consistency_rollup")
    consistency_rollup = consistency_rollup if isinstance(consistency_rollup, dict) else {}
    reconnect_rollup = governance.get("reconnect_rollup")
    reconnect_rollup = reconnect_rollup if isinstance(reconnect_rollup, dict) else {}
    evaluation_rollup = governance.get("evaluation_summary")
    evaluation_rollup = evaluation_rollup if isinstance(evaluation_rollup, dict) else {}
    restartability = _build_restartability_diagnostics(status_payload)
    restart_observation = _build_restart_observation_diagnostics(status_payload)
    restart_backoff = _build_restart_backoff_diagnostics(status_payload)
    statefile_ownership = _build_statefile_ownership_diagnostics(status_payload)

    diagnostics = {
        "has_control_rollup": bool(control_rollup),
        "has_consistency_rollup": bool(consistency_rollup),
        "has_reconnect_rollup": bool(reconnect_rollup),
        "has_evaluation_rollup": bool(evaluation_rollup),
        "has_mismatch": bool(consistency_rollup.get("has_mismatch")),
        "requires_manual_review": bool(governance.get("requires_manual_review")),
        "staleness_evaluated": bool(governance.get("staleness_evaluated")),
        "has_reconnect_failures": bool(reconnect_rollup.get("has_reconnect_failures")),
        "has_reconnect_last_error": bool(reconnect_rollup.get("has_last_error")),
        "has_stale_component": bool(evaluation_rollup.get("has_stale_component")),
        "has_not_evaluated_component": bool(evaluation_rollup.get("has_not_evaluated_component")),
        "all_components_evaluated": bool(evaluation_rollup.get("all_components_evaluated")),
        "restartability": restartability,
        "restart_observation": restart_observation,
        "restart_backoff": restart_backoff,
        "boundary": governance.get("boundary"),
    }
    if statefile_ownership is not None:
        diagnostics["statefile_ownership"] = statefile_ownership
    return diagnostics


def _build_statefile_ownership_diagnostics(status_payload: dict[str, Any] | None) -> dict[str, Any] | None:
    payload = status_payload if isinstance(status_payload, dict) else {}
    statefile_ownership = payload.get("statefile_ownership")
    if not isinstance(statefile_ownership, dict):
        return None
    compact: dict[str, Any] = {}
    for key in (
        "schema_version",
        "status",
        "reason_codes",
        "statefile_exists",
        "pidfile_exists",
        "lockfile_exists",
        "active",
        "control_state",
        "payload_pid",
        "owned_pid",
        "pid_matches_owned_state",
        "process_alive",
        "boundary",
    ):
        if key in statefile_ownership:
            compact[key] = statefile_ownership[key]
    return compact


def _build_restartability_diagnostics(status_payload: dict[str, Any] | None) -> dict[str, Any]:
    payload = status_payload if isinstance(status_payload, dict) else {}
    control = payload.get("control")
    control = control if isinstance(control, dict) else {}
    state = control.get("state")
    active = bool(control.get("active")) and state in {"starting", "running", "reconnecting", "degraded", "stopping"}
    start_request = control.get("start_request")
    restart_backoff = _build_restart_backoff_diagnostics(status_payload)
    reason_codes: list[str] = []
    if bool(restart_backoff.get("active")):
        reason_codes.append("BACKOFF_ACTIVE")
    elif not active:
        reason_codes.append("NO_ACTIVE_RUN")
    elif not isinstance(start_request, dict):
        reason_codes.append("MISSING_START_REQUEST")
    elif not _restartability_start_request_valid(start_request):
        reason_codes.append("INVALID_START_REQUEST")
    ready = not reason_codes
    return {
        "ready": ready,
        "decision": "ready" if ready else "blocked",
        "reason_codes": reason_codes,
        "has_start_request": isinstance(start_request, dict),
        "start_request_summary": _restartability_start_request_summary(start_request),
        "boundary": RESTARTABILITY_BOUNDARY,
    }


def _restartability_start_request_summary(start_request: Any) -> dict[str, Any] | None:
    if not isinstance(start_request, dict):
        return None
    stock_list = start_request.get("stock_list")
    return {
        "stock_count": len(stock_list) if isinstance(stock_list, list) else 0,
        "has_max_events": start_request.get("max_events") is not None,
        "has_max_seconds": start_request.get("max_seconds") is not None,
        "has_poll_interval": start_request.get("poll_interval") is not None,
    }


def _restartability_start_request_valid(start_request: dict[str, Any]) -> bool:
    stock_list = start_request.get("stock_list")
    max_events = start_request.get("max_events")
    max_seconds = start_request.get("max_seconds")
    poll_interval = start_request.get("poll_interval")
    if not isinstance(stock_list, list) or not stock_list or not all(isinstance(item, str) for item in stock_list):
        return False
    if max_events is not None and (isinstance(max_events, bool) or not isinstance(max_events, int) or max_events <= 0):
        return False
    if max_seconds is not None and (
        isinstance(max_seconds, bool) or not isinstance(max_seconds, (int, float)) or max_seconds <= 0
    ):
        return False
    if poll_interval is not None and (
        isinstance(poll_interval, bool) or not isinstance(poll_interval, (int, float)) or poll_interval < 0
    ):
        return False
    return True


def _build_restart_observation_diagnostics(status_payload: dict[str, Any] | None) -> dict[str, Any]:
    payload = status_payload if isinstance(status_payload, dict) else {}
    control = payload.get("control")
    control = control if isinstance(control, dict) else {}
    observation = control.get("last_restart_observation")
    if not isinstance(observation, dict):
        return {"has_observation": False}

    start_request_summary = observation.get("start_request_summary")
    if isinstance(start_request_summary, dict):
        start_request_summary = dict(start_request_summary)
    else:
        start_request_summary = None

    return {
        "has_observation": True,
        "status": observation.get("status"),
        "previous_run_id": observation.get("previous_run_id"),
        "new_run_id": observation.get("new_run_id"),
        "reason": observation.get("reason"),
        "stop_state": observation.get("stop_state"),
        "start_state": observation.get("start_state"),
        "start_request_summary": start_request_summary,
        "boundary": observation.get("boundary"),
    }


def _build_restart_backoff_diagnostics(status_payload: dict[str, Any] | None) -> dict[str, Any]:
    payload = status_payload if isinstance(status_payload, dict) else {}
    control = payload.get("control")
    control = control if isinstance(control, dict) else {}
    restart_backoff = control.get("restart_backoff")
    if not isinstance(restart_backoff, dict) or not _restart_backoff_is_active(restart_backoff):
        return {"active": False}

    start_request_summary = restart_backoff.get("start_request_summary")
    if isinstance(start_request_summary, dict):
        start_request_summary = dict(start_request_summary)
    else:
        start_request_summary = None

    reason_codes = restart_backoff.get("reason_codes")
    if isinstance(reason_codes, list):
        reason_codes = [str(item) for item in reason_codes if isinstance(item, str)]
    else:
        reason_codes = ["BACKOFF_ACTIVE"]

    return {
        "active": True,
        "status": restart_backoff.get("status"),
        "reason_codes": reason_codes,
        "previous_run_id": restart_backoff.get("previous_run_id"),
        "reason": restart_backoff.get("reason"),
        "created_at": restart_backoff.get("created_at"),
        "retry_after_at": restart_backoff.get("retry_after_at"),
        "backoff_seconds": restart_backoff.get("backoff_seconds"),
        "start_error_code": restart_backoff.get("start_error_code"),
        "start_request_summary": start_request_summary,
        "boundary": restart_backoff.get("boundary"),
    }


def _restart_backoff_is_active(restart_backoff: dict[str, Any]) -> bool:
    retry_after_at = restart_backoff.get("retry_after_at")
    if not isinstance(retry_after_at, str):
        return False
    try:
        parsed = retry_after_at
        if parsed.endswith("Z"):
            parsed = f"{parsed[:-1]}+00:00"
        retry_after_dt = datetime.fromisoformat(parsed)
    except ValueError:
        return False
    if retry_after_dt.tzinfo is None:
        retry_after_dt = retry_after_dt.replace(tzinfo=timezone.utc)
    return retry_after_dt.astimezone(timezone.utc) > datetime.now(timezone.utc)
