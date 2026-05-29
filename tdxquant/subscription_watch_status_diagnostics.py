from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


RESTARTABILITY_BOUNDARY = "read_only;does_not_stop_start_or_schedule_restart"
OPERATOR_RUNBOOK_SCHEMA_VERSION = "tdx.subscription_watch.operator_runbook.v1"
OPERATOR_RUNBOOK_BOUNDARY = "read_only_operator_runbook;does_not_execute_lifecycle_control"


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
    lifecycle_readiness = _build_lifecycle_readiness_diagnostics(summary_view)
    restartability = _build_restartability_diagnostics(status_payload)
    restart_observation = _build_restart_observation_diagnostics(status_payload)
    supervisor_run_observation = _build_supervisor_run_observation_diagnostics(status_payload)
    supervisor_tick_observation = _build_supervisor_tick_observation_diagnostics(status_payload)
    restart_backoff = _build_restart_backoff_diagnostics(status_payload)
    statefile_ownership = _build_statefile_ownership_diagnostics(status_payload)
    supervisor_daemon = summary_view.get("supervisor_daemon")
    supervisor_daemon = supervisor_daemon if isinstance(supervisor_daemon, dict) else None

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
        "lifecycle_readiness": lifecycle_readiness,
        "restart_observation": restart_observation,
        "restart_backoff": restart_backoff,
        "boundary": governance.get("boundary"),
    }
    if supervisor_run_observation is not None:
        diagnostics["supervisor_run_observation"] = supervisor_run_observation
    if supervisor_tick_observation is not None:
        diagnostics["supervisor_tick_observation"] = supervisor_tick_observation
    if statefile_ownership is not None:
        diagnostics["statefile_ownership"] = statefile_ownership
    if supervisor_daemon is not None:
        diagnostics["supervisor_daemon"] = dict(supervisor_daemon)
    return diagnostics


def build_subscription_watch_status_runbook(diagnostics_view: dict[str, Any]) -> dict[str, Any]:
    """Build a compact read-only operator checklist from an existing diagnostics view."""
    diagnostics = diagnostics_view.get("diagnostics")
    diagnostics = diagnostics if isinstance(diagnostics, dict) else {}
    lifecycle_readiness = diagnostics.get("lifecycle_readiness")
    lifecycle_readiness = lifecycle_readiness if isinstance(lifecycle_readiness, dict) else {}
    restart_backoff = diagnostics.get("restart_backoff")
    restart_backoff = restart_backoff if isinstance(restart_backoff, dict) else {}

    lifecycle_ready = lifecycle_readiness.get("ready")
    lifecycle_decision = lifecycle_readiness.get("decision")
    lifecycle_reason_codes = lifecycle_readiness.get("reason_codes")
    lifecycle_reason_codes = list(lifecycle_reason_codes) if isinstance(lifecycle_reason_codes, list) else []
    lifecycle_status = "passed" if lifecycle_ready is True else "blocked"

    manual_review_required = bool(diagnostics.get("requires_manual_review"))
    has_mismatch = bool(diagnostics.get("has_mismatch"))
    has_stale_component = bool(diagnostics.get("has_stale_component"))
    has_not_evaluated_component = bool(diagnostics.get("has_not_evaluated_component"))
    restart_backoff_active = bool(restart_backoff.get("active"))
    staleness_status = "blocked" if has_stale_component else "observe" if has_not_evaluated_component else "passed"

    checks = [
        {
            "code": "lifecycle_readiness",
            "status": lifecycle_status,
            "decision": lifecycle_decision,
            "reason_codes": lifecycle_reason_codes,
            "action": "none" if lifecycle_status == "passed" else "review_lifecycle_readiness",
        },
        {
            "code": "governance_review",
            "status": "blocked" if manual_review_required else "passed",
            "requires_manual_review": manual_review_required,
            "action": "review_governance_reasons" if manual_review_required else "none",
        },
        {
            "code": "runtime_consistency",
            "status": "blocked" if has_mismatch else "passed",
            "has_mismatch": has_mismatch,
            "action": "compare_control_and_watch_status" if has_mismatch else "none",
        },
        {
            "code": "staleness",
            "status": staleness_status,
            "has_stale_component": has_stale_component,
            "has_not_evaluated_component": has_not_evaluated_component,
            "action": "review_stale_components" if has_stale_component else "inspect_not_evaluated_components"
            if has_not_evaluated_component
            else "none",
        },
        {
            "code": "restart_backoff",
            "status": "blocked" if restart_backoff_active else "passed",
            "active": restart_backoff_active,
            "action": "wait_for_restart_backoff" if restart_backoff_active else "none",
        },
    ]
    blocking_check_count = sum(1 for check in checks if check.get("status") == "blocked")
    has_observe_check = any(check.get("status") == "observe" for check in checks)
    if blocking_check_count:
        decision = "blocked"
    elif has_observe_check:
        decision = "observe"
    else:
        decision = "ready"
    return {
        "schema_version": OPERATOR_RUNBOOK_SCHEMA_VERSION,
        "decision": decision,
        "manual_review_required": manual_review_required,
        "check_count": len(checks),
        "blocking_check_count": blocking_check_count,
        "checks": checks,
        "boundary": OPERATOR_RUNBOOK_BOUNDARY,
    }


def _build_lifecycle_readiness_diagnostics(summary_view: dict[str, Any]) -> dict[str, Any] | None:
    status_summary = summary_view.get("status_summary")
    status_summary = status_summary if isinstance(status_summary, dict) else {}
    lifecycle_readiness = status_summary.get("lifecycle_readiness")
    if not isinstance(lifecycle_readiness, dict):
        return None

    compact: dict[str, Any] = {}
    for key in (
        "schema_version",
        "ready",
        "decision",
        "run_id",
        "state",
        "active",
        "has_start_request",
        "restart_backoff_active",
        "statefile_ownership_status",
        "statefile_pid_matches_owned_state",
        "statefile_process_alive",
        "supervisor_daemon_status",
        "supervisor_daemon_control_allowed",
        "boundary",
    ):
        if key in lifecycle_readiness:
            compact[key] = lifecycle_readiness[key]

    reason_codes = lifecycle_readiness.get("reason_codes")
    compact["reason_codes"] = list(reason_codes) if isinstance(reason_codes, list) else []
    start_request_summary = lifecycle_readiness.get("start_request_summary")
    compact["start_request_summary"] = dict(start_request_summary) if isinstance(start_request_summary, dict) else None
    return compact


def _build_supervisor_tick_observation_diagnostics(status_payload: dict[str, Any] | None) -> dict[str, Any] | None:
    payload = status_payload if isinstance(status_payload, dict) else {}
    control = payload.get("control")
    control = control if isinstance(control, dict) else {}
    observation = control.get("last_supervisor_tick_observation")
    if not isinstance(observation, dict):
        return None
    compact: dict[str, Any] = {}
    for key in (
        "schema_version",
        "status",
        "decision",
        "action_taken",
        "reason_codes",
        "previous_run_id",
        "new_run_id",
        "start_request_summary",
        "error_code",
        "reason",
        "boundary",
    ):
        if key in observation:
            compact[key] = observation[key]
    return compact


def _build_supervisor_run_observation_diagnostics(status_payload: dict[str, Any] | None) -> dict[str, Any] | None:
    payload = status_payload if isinstance(status_payload, dict) else {}
    control = payload.get("control")
    control = control if isinstance(control, dict) else {}
    observation = control.get("last_supervisor_run_observation")
    if not isinstance(observation, dict):
        return None
    compact: dict[str, Any] = {}
    for key in (
        "schema_version",
        "status",
        "final_status",
        "final_decision",
        "tick_count",
        "max_ticks",
        "interval_seconds",
        "reason",
        "action_taken",
        "tick_status_counts",
        "tick_decision_counts",
        "previous_run_id",
        "new_run_id",
        "boundary",
    ):
        if key in observation:
            compact[key] = observation[key]
    return compact


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
