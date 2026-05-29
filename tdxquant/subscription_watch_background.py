from __future__ import annotations

from dataclasses import dataclass
import errno
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import threading
import time
from datetime import datetime, timezone
from typing import Any

from .subscription_watch_run import build_subscription_watch_run_paths

DEFAULT_STOP_GRACE_PERIOD_SECONDS = 5
DEFAULT_START_TIMEOUT_SECONDS = 10
DEFAULT_STOP_FORCE_KILL_TIMEOUT_SECONDS = 2
ACTIVE_PROCESS_STATES = {"starting", "running", "reconnecting", "degraded", "stopping"}
SUBSCRIPTION_WATCH_STATUS_SUMMARY_SCHEMA_VERSION = "tdx.subscription_watch.status_summary.v1"
SUBSCRIPTION_WATCH_GOVERNANCE_BOUNDARY = (
    "advisory_only; does_not_trigger_reconnect_backoff_restart_or_lifecycle_changes"
)


def build_subscription_watch_status_summary(
    *,
    control: dict[str, Any] | None,
    watch_status: dict[str, Any] | None,
    heartbeat_stale_after_seconds: float | int | None = None,
    watermark_stale_after_seconds: float | int | None = None,
    reconnect_stale_after_seconds: float | int | None = None,
    now_utc: datetime | str | None = None,
) -> dict[str, Any]:
    resolved_control = control if isinstance(control, dict) else {}
    resolved_status = watch_status if isinstance(watch_status, dict) else {}
    state = _optional_str(resolved_status.get("state")) or _optional_str(resolved_control.get("state")) or "unknown"
    run_id = _optional_str(resolved_status.get("run_id")) or _optional_str(resolved_control.get("run_id"))
    active = bool(resolved_control.get("active"))
    heartbeat = _build_heartbeat_summary(
        heartbeat_at=_optional_str(resolved_status.get("heartbeat_at")),
        heartbeat_stale_after_seconds=heartbeat_stale_after_seconds,
        now_utc=now_utc,
    )
    watermark = _build_watermark_summary(
        event_count=_optional_int(resolved_status.get("event_count"), default=0),
        unique_symbol_count=_optional_int(resolved_status.get("unique_symbol_count"), default=0),
        last_sequence=_optional_int_or_none(resolved_status.get("last_sequence")),
        last_event_ts=_optional_str(resolved_status.get("last_event_ts"))
        or _optional_str(resolved_status.get("last_event_at")),
        last_symbol=_optional_str(resolved_status.get("last_symbol")),
        last_source_ts=_optional_str(resolved_status.get("last_source_ts")),
        watermark_stale_after_seconds=watermark_stale_after_seconds,
        now_utc=now_utc,
    )
    overall_status = _subscription_watch_overall_status(state=state, active=active)
    reconnect = _build_reconnect_summary(
        reconnect_count=_optional_int(resolved_status.get("reconnect_count"), default=0),
        last_disconnect_at=_optional_str(resolved_status.get("last_disconnect_at")),
        last_reconnect_at=_optional_str(resolved_status.get("last_reconnect_at")),
        next_reconnect_at=_optional_str(resolved_status.get("next_reconnect_at")),
        degraded_since=_optional_str(resolved_status.get("degraded_since")),
        consecutive_reconnect_failures=_optional_int(
            resolved_status.get("consecutive_reconnect_failures"),
            default=0,
        ),
        last_error=resolved_status.get("last_error") if isinstance(resolved_status.get("last_error"), dict) else None,
        overall_status=overall_status,
        reconnect_stale_after_seconds=reconnect_stale_after_seconds,
        now_utc=now_utc,
    )
    return {
        "schema_version": SUBSCRIPTION_WATCH_STATUS_SUMMARY_SCHEMA_VERSION,
        "overall_status": overall_status,
        "state": state,
        "active": active,
        "run_id": run_id,
        "control_rollup": _build_subscription_watch_control_rollup(resolved_control),
        "consistency_rollup": _build_subscription_watch_consistency_rollup(
            control=resolved_control,
            watch_status=resolved_status,
        ),
        "heartbeat": heartbeat,
        "watermark": watermark,
        "reconnect": reconnect,
        "governance": _build_subscription_watch_governance_summary(
            overall_status=overall_status,
            heartbeat=heartbeat,
            watermark=watermark,
            reconnect=reconnect,
        ),
        "boundary": "summary_projection_only; optional heartbeat/watermark/reconnect staleness evaluation only; does not change reconnect/backoff behavior",
    }


def _build_heartbeat_summary(
    *,
    heartbeat_at: str | None,
    heartbeat_stale_after_seconds: float | int | None,
    now_utc: datetime | str | None,
) -> dict[str, Any]:
    heartbeat = {
        "status": "present" if heartbeat_at else "missing",
        "heartbeat_at": heartbeat_at,
        "staleness": "not_evaluated",
    }
    if not heartbeat_at or heartbeat_stale_after_seconds is None:
        return heartbeat
    try:
        stale_after_seconds = float(heartbeat_stale_after_seconds)
    except (TypeError, ValueError):
        heartbeat["staleness"] = "invalid_threshold"
        return heartbeat
    if stale_after_seconds <= 0:
        heartbeat["staleness"] = "invalid_threshold"
        heartbeat["stale_after_seconds"] = stale_after_seconds
        return heartbeat
    try:
        heartbeat_dt = _parse_rfc3339_datetime(heartbeat_at)
        evaluated_at_dt = _coerce_utc_datetime(now_utc)
    except ValueError:
        heartbeat["staleness"] = "invalid_timestamp"
        heartbeat["stale_after_seconds"] = stale_after_seconds
        return heartbeat
    age_seconds = max(0.0, (evaluated_at_dt - heartbeat_dt).total_seconds())
    heartbeat.update(
        {
            "staleness": "stale" if age_seconds > stale_after_seconds else "fresh",
            "age_seconds": age_seconds,
            "stale_after_seconds": stale_after_seconds,
            "evaluated_at": evaluated_at_dt.isoformat(),
        }
    )
    return heartbeat


def _build_watermark_summary(
    *,
    event_count: int,
    unique_symbol_count: int,
    last_sequence: int | None,
    last_event_ts: str | None,
    last_symbol: str | None,
    last_source_ts: str | None,
    watermark_stale_after_seconds: float | int | None,
    now_utc: datetime | str | None,
) -> dict[str, Any]:
    watermark: dict[str, Any] = {
        "event_count": event_count,
        "unique_symbol_count": unique_symbol_count,
        "last_sequence": last_sequence,
        "last_event_ts": last_event_ts,
        "last_symbol": last_symbol,
        "last_source_ts": last_source_ts,
        "staleness": "not_evaluated",
    }
    if watermark_stale_after_seconds is None:
        return watermark
    try:
        stale_after_seconds = float(watermark_stale_after_seconds)
    except (TypeError, ValueError):
        watermark["staleness"] = "invalid_threshold"
        return watermark
    if stale_after_seconds <= 0:
        watermark["staleness"] = "invalid_threshold"
        watermark["stale_after_seconds"] = stale_after_seconds
        return watermark
    if not last_event_ts:
        watermark["staleness"] = "missing"
        watermark["stale_after_seconds"] = stale_after_seconds
        return watermark
    try:
        watermark_dt = _parse_rfc3339_datetime(last_event_ts)
        evaluated_at_dt = _coerce_utc_datetime(now_utc)
    except ValueError:
        watermark["staleness"] = "invalid_timestamp"
        watermark["stale_after_seconds"] = stale_after_seconds
        return watermark
    age_seconds = max(0.0, (evaluated_at_dt - watermark_dt).total_seconds())
    watermark.update(
        {
            "staleness": "stale" if age_seconds > stale_after_seconds else "fresh",
            "age_seconds": age_seconds,
            "stale_after_seconds": stale_after_seconds,
            "evaluated_at": evaluated_at_dt.isoformat(),
        }
    )
    return watermark


def _build_reconnect_summary(
    *,
    reconnect_count: int,
    last_disconnect_at: str | None,
    last_reconnect_at: str | None,
    next_reconnect_at: str | None,
    degraded_since: str | None,
    consecutive_reconnect_failures: int,
    last_error: dict[str, Any] | None,
    overall_status: str,
    reconnect_stale_after_seconds: float | int | None,
    now_utc: datetime | str | None,
) -> dict[str, Any]:
    reconnect: dict[str, Any] = {
        "reconnect_count": reconnect_count,
        "last_disconnect_at": last_disconnect_at,
        "last_reconnect_at": last_reconnect_at,
        "next_reconnect_at": next_reconnect_at,
        "degraded_since": degraded_since,
        "consecutive_reconnect_failures": consecutive_reconnect_failures,
        "last_error": last_error,
        "staleness": "not_evaluated",
    }
    if reconnect_stale_after_seconds is None:
        return reconnect
    try:
        stale_after_seconds = float(reconnect_stale_after_seconds)
    except (TypeError, ValueError):
        reconnect["staleness"] = "invalid_threshold"
        return reconnect
    if stale_after_seconds <= 0:
        reconnect["staleness"] = "invalid_threshold"
        reconnect["stale_after_seconds"] = stale_after_seconds
        return reconnect
    reconnect["stale_after_seconds"] = stale_after_seconds
    if overall_status not in {"reconnecting", "degraded"}:
        reconnect["staleness"] = "not_applicable"
        return reconnect

    age_source = "last_disconnect_at" if last_disconnect_at else "degraded_since" if degraded_since else None
    if age_source is None:
        reconnect["staleness"] = "missing"
        reconnect["age_source"] = None
        return reconnect
    source_ts = last_disconnect_at if age_source == "last_disconnect_at" else degraded_since
    try:
        source_dt = _parse_rfc3339_datetime(source_ts or "")
        evaluated_at_dt = _coerce_utc_datetime(now_utc)
    except ValueError:
        reconnect["staleness"] = "invalid_timestamp"
        reconnect["age_source"] = age_source
        return reconnect
    age_seconds = max(0.0, (evaluated_at_dt - source_dt).total_seconds())
    reconnect.update(
        {
            "staleness": "stale" if age_seconds > stale_after_seconds else "fresh",
            "age_seconds": age_seconds,
            "age_source": age_source,
            "evaluated_at": evaluated_at_dt.isoformat(),
        }
    )
    return reconnect


def _build_subscription_watch_governance_summary(
    *,
    overall_status: str,
    heartbeat: dict[str, Any],
    watermark: dict[str, Any],
    reconnect: dict[str, Any],
) -> dict[str, Any]:
    reasons: list[str] = []
    if overall_status in {"reconnecting", "degraded", "failed"}:
        reasons.append(f"overall_status:{overall_status}")

    staleness_evaluated = False
    for name, summary in (("heartbeat", heartbeat), ("watermark", watermark), ("reconnect", reconnect)):
        staleness = summary.get("staleness")
        if staleness != "not_evaluated":
            staleness_evaluated = True
        if staleness == "stale":
            reasons.append(f"{name}:stale")

    requires_manual_review = bool(reasons)
    actions = _build_subscription_watch_governance_actions(reasons)
    reason_source_counts = _build_subscription_watch_governance_reason_source_counts(reasons)
    return {
        "decision": "manual_review" if requires_manual_review else "observe",
        "requires_manual_review": requires_manual_review,
        "reasons": reasons,
        "reason_count": len(reasons),
        "reason_source_counts": reason_source_counts,
        "reason_source_key_count": len(reason_source_counts),
        "reason_summary": _build_subscription_watch_governance_reason_summary(reasons),
        "actions": actions,
        "action_count": len(actions),
        "action_summary": _build_subscription_watch_governance_action_summary(actions),
        "reconnect_rollup": _build_subscription_watch_governance_reconnect_rollup(
            reconnect
        ),
        "evaluation_summary": _build_subscription_watch_governance_evaluation_summary(
            heartbeat=heartbeat,
            watermark=watermark,
            reconnect=reconnect,
        ),
        "staleness_evaluated": staleness_evaluated,
        "boundary": SUBSCRIPTION_WATCH_GOVERNANCE_BOUNDARY,
    }


def _build_subscription_watch_governance_reason_source_counts(reasons: list[Any]) -> dict[str, int]:
    source_counts: dict[str, int] = {}
    for reason in reasons:
        source = _subscription_watch_governance_reason_source(reason)
        source_counts[source] = source_counts.get(source, 0) + 1
    return {source: source_counts[source] for source in sorted(source_counts)}


def _build_subscription_watch_governance_reason_summary(reasons: list[Any]) -> dict[str, Any]:
    primary_reason = reasons[0] if reasons and isinstance(reasons[0], str) else None
    primary_source = (
        _subscription_watch_governance_reason_source(primary_reason) if primary_reason is not None else None
    )
    source_counts = _build_subscription_watch_governance_reason_source_counts(reasons)
    reason_code_counts = _build_subscription_watch_governance_reason_code_counts(reasons)
    return {
        "count": len(reasons),
        "primary_reason": primary_reason,
        "primary_source": primary_source,
        "primary_reason_source": primary_source,
        "source_counts": source_counts,
        "source_key_count": len(source_counts),
        "reason_code_counts": reason_code_counts,
        "reason_code_key_count": len(reason_code_counts),
    }


def _build_subscription_watch_governance_reason_code_counts(reasons: list[Any]) -> dict[str, int]:
    reason_code_counts: dict[str, int] = {}
    for reason in reasons:
        if not isinstance(reason, str) or not reason:
            continue
        reason_code_counts[reason] = reason_code_counts.get(reason, 0) + 1
    return {reason: reason_code_counts[reason] for reason in sorted(reason_code_counts)}


def _subscription_watch_governance_reason_source(reason: Any) -> str:
    if isinstance(reason, str) and ":" in reason:
        candidate = reason.split(":", maxsplit=1)[0].strip()
        if candidate:
            return candidate
    return "unknown"


def _build_subscription_watch_control_rollup(control: dict[str, Any]) -> dict[str, Any]:
    control_state = _optional_str(control.get("state")) or "unknown"
    control_run_id = _optional_str(control.get("run_id"))
    control_pid = _optional_int_or_none(control.get("pid"))
    control_reason = _optional_str(control.get("reason"))
    return {
        "control_state": control_state,
        "control_active": bool(control.get("active")),
        "has_control_run_id": control_run_id is not None,
        "has_control_pid": _positive_non_bool_int(control_pid),
        "control_reason": control_reason,
        "has_control_reason": control_reason is not None,
        "stale_process_state": control_reason == "stale_process_state",
        "startup_persistence_failed": control_reason == "startup_persistence_failed",
    }


def _build_subscription_watch_consistency_rollup(
    *,
    control: dict[str, Any],
    watch_status: dict[str, Any],
) -> dict[str, Any]:
    control_state = _optional_str(control.get("state")) or "unknown"
    watch_state = _optional_str(watch_status.get("state"))
    control_run_id = _optional_str(control.get("run_id"))
    watch_run_id = _optional_str(watch_status.get("run_id"))
    control_pid = _optional_int_or_none(control.get("pid"))
    state_match = control_state == watch_state if watch_state is not None else None
    run_id_match = (
        control_run_id == watch_run_id
        if control_run_id is not None and watch_run_id is not None
        else None
    )
    return {
        "control_state": control_state,
        "watch_state": watch_state,
        "has_watch_status": bool(watch_status),
        "has_control_run_id": control_run_id is not None,
        "has_watch_run_id": watch_run_id is not None,
        "run_id_match": run_id_match,
        "state_match": state_match,
        "has_control_pid": _positive_non_bool_int(control_pid),
        "has_mismatch": state_match is False or run_id_match is False,
    }


def _positive_non_bool_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _build_subscription_watch_governance_reconnect_rollup(
    reconnect: dict[str, Any],
) -> dict[str, Any]:
    reconnect_count = reconnect.get("reconnect_count")
    consecutive_reconnect_failures = reconnect.get("consecutive_reconnect_failures")
    last_error = reconnect.get("last_error")
    next_reconnect_at = reconnect.get("next_reconnect_at")
    return {
        "staleness": reconnect.get("staleness"),
        "reconnect_count": reconnect_count,
        "consecutive_reconnect_failures": consecutive_reconnect_failures,
        "has_reconnects": _positive_non_bool_int(reconnect_count),
        "has_reconnect_failures": _positive_non_bool_int(
            consecutive_reconnect_failures
        ),
        "has_last_error": isinstance(last_error, dict) and bool(last_error),
        "has_next_reconnect_at": isinstance(next_reconnect_at, str)
        and bool(next_reconnect_at),
        "age_source": reconnect.get("age_source"),
        "stale_after_seconds": reconnect.get("stale_after_seconds"),
    }


def _build_subscription_watch_governance_evaluation_summary(
    *,
    heartbeat: dict[str, Any],
    watermark: dict[str, Any],
    reconnect: dict[str, Any],
) -> dict[str, Any]:
    evaluated_components: list[str] = []
    stale_components: list[str] = []
    fresh_components: list[str] = []
    not_evaluated_components: list[str] = []
    component_status_counts: dict[str, int] = {}
    evaluated_status_counts: dict[str, int] = {}
    for name, summary in (("heartbeat", heartbeat), ("watermark", watermark), ("reconnect", reconnect)):
        staleness = summary.get("staleness")
        component_status = staleness if isinstance(staleness, str) and staleness else "unknown"
        component_status_counts[component_status] = component_status_counts.get(component_status, 0) + 1
        if staleness == "not_evaluated":
            not_evaluated_components.append(name)
        else:
            evaluated_components.append(name)
            evaluated_status_counts[component_status] = evaluated_status_counts.get(component_status, 0) + 1
        if staleness == "stale":
            stale_components.append(name)
        if staleness == "fresh":
            fresh_components.append(name)

    return {
        "evaluated_components": evaluated_components,
        "primary_evaluated_component": evaluated_components[0] if evaluated_components else None,
        "stale_components": stale_components,
        "primary_stale_component": stale_components[0] if stale_components else None,
        "has_stale_component": bool(stale_components),
        "fresh_components": fresh_components,
        "primary_fresh_component": fresh_components[0] if fresh_components else None,
        "has_fresh_component": bool(fresh_components),
        "not_evaluated_components": not_evaluated_components,
        "primary_not_evaluated_component": not_evaluated_components[0]
        if not_evaluated_components
        else None,
        "has_not_evaluated_component": bool(not_evaluated_components),
        "all_components_evaluated": not bool(not_evaluated_components),
        "evaluated_count": len(evaluated_components),
        "stale_count": len(stale_components),
        "fresh_count": len(fresh_components),
        "not_evaluated_count": len(not_evaluated_components),
        "component_status_counts": {
            status: component_status_counts[status] for status in sorted(component_status_counts)
        },
        "component_status_key_count": len(component_status_counts),
        "evaluated_status_counts": {
            status: evaluated_status_counts[status] for status in sorted(evaluated_status_counts)
        },
        "evaluated_status_key_count": len(evaluated_status_counts),
    }


def _build_subscription_watch_governance_action_summary(actions: list[dict[str, str]]) -> dict[str, Any]:
    first_action = actions[0] if actions else None
    primary_reason = first_action.get("reason") if first_action else None
    primary_severity = first_action.get("severity") if first_action else "none"
    severity_counts: dict[str, int] = {}
    action_name_counts: dict[str, int] = {}
    reason_source_counts: dict[str, int] = {}
    reason_code_counts: dict[str, int] = {}
    for action in actions:
        severity = action.get("severity")
        if severity:
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        action_name = action.get("action")
        if action_name:
            action_name_counts[action_name] = action_name_counts.get(action_name, 0) + 1
        action_reason = action.get("reason")
        reason_source = _subscription_watch_governance_reason_source(action_reason)
        reason_source_counts[reason_source] = reason_source_counts.get(reason_source, 0) + 1
        if isinstance(action_reason, str) and action_reason:
            reason_code_counts[action_reason] = reason_code_counts.get(action_reason, 0) + 1
    return {
        "count": len(actions),
        "primary_action": first_action.get("action") if first_action else None,
        "primary_reason": primary_reason,
        "primary_reason_source": (
            _subscription_watch_governance_reason_source(primary_reason)
            if isinstance(primary_reason, str) and primary_reason
            else None
        ),
        "primary_severity": primary_severity,
        "severity": primary_severity,
        "severity_counts": {severity: severity_counts[severity] for severity in sorted(severity_counts)},
        "severity_key_count": len(severity_counts),
        "action_name_counts": {
            action_name: action_name_counts[action_name] for action_name in sorted(action_name_counts)
        },
        "action_name_key_count": len(action_name_counts),
        "reason_source_counts": {
            reason_source: reason_source_counts[reason_source] for reason_source in sorted(reason_source_counts)
        },
        "reason_source_key_count": len(reason_source_counts),
        "reason_code_counts": {reason: reason_code_counts[reason] for reason in sorted(reason_code_counts)},
        "reason_code_key_count": len(reason_code_counts),
    }


def _build_subscription_watch_governance_actions(reasons: list[str]) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for reason in reasons:
        if reason.startswith("overall_status:"):
            status = reason.split(":", maxsplit=1)[1]
            actions.append(
                {
                    "action": "review_subscription_watch_resilience",
                    "reason": reason,
                    "severity": "review",
                    "description": f"Inspect subscription-watch long-run process health for {status} status.",
                }
            )
        elif reason == "heartbeat:stale":
            actions.append(
                {
                    "action": "review_subscription_watch_heartbeat",
                    "reason": reason,
                    "severity": "review",
                    "description": "Inspect heartbeat freshness before changing reconnect or restart behavior.",
                }
            )
        elif reason == "watermark:stale":
            actions.append(
                {
                    "action": "review_subscription_watch_watermark",
                    "reason": reason,
                    "severity": "review",
                    "description": "Inspect event watermark freshness before changing reconnect or restart behavior.",
                }
            )
        elif reason == "reconnect:stale":
            actions.append(
                {
                    "action": "review_subscription_watch_reconnect",
                    "reason": reason,
                    "severity": "review",
                    "description": "Inspect reconnect/degraded duration before changing reconnect or restart behavior.",
                }
            )
        else:
            actions.append(
                {
                    "action": "review_subscription_watch_status",
                    "reason": reason,
                    "severity": "review",
                    "description": "Inspect subscription-watch status before changing reconnect or restart behavior.",
                }
            )
    return actions


def _coerce_utc_datetime(value: datetime | str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if isinstance(value, datetime):
        candidate = value
    else:
        candidate = _parse_rfc3339_datetime(value)
    if candidate.tzinfo is None:
        candidate = candidate.replace(tzinfo=timezone.utc)
    return candidate.astimezone(timezone.utc)


def _parse_rfc3339_datetime(value: str) -> datetime:
    text = str(value).strip()
    if not text:
        raise ValueError("empty timestamp")
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"invalid timestamp: {value}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _subscription_watch_overall_status(*, state: str, active: bool) -> str:
    if state in {"reconnecting", "degraded", "failed", "completed", "stopped"}:
        return state
    if active and state in ACTIVE_PROCESS_STATES:
        return "active"
    if state in {"starting", "running", "stopping"}:
        return "active"
    return "unknown"


def _optional_str(value: Any) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None


def _optional_int(value: Any, *, default: int) -> int:
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _optional_int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class SubscriptionWatchBackgroundPaths:
    root_dir: Path
    active_path: Path
    pid_path: Path
    lock_path: Path


def build_background_paths(root_dir: Path) -> SubscriptionWatchBackgroundPaths:
    return SubscriptionWatchBackgroundPaths(
        root_dir=root_dir,
        active_path=root_dir / "active.json",
        pid_path=root_dir / "pid",
        lock_path=root_dir / "lock",
    )


def _pid_is_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _parse_pid(raw_pid: Any) -> int:
    try:
        return int(raw_pid or 0)
    except (TypeError, ValueError):
        return 0


def _cleanup_owned_state(paths: SubscriptionWatchBackgroundPaths) -> None:
    if paths.pid_path.exists():
        paths.pid_path.unlink()


def _cleanup_start_failure_state(
    paths: SubscriptionWatchBackgroundPaths,
    *,
    previous_active_payload: dict[str, Any] | None,
) -> None:
    _cleanup_owned_state(paths)
    if previous_active_payload is None:
        if paths.active_path.exists():
            paths.active_path.unlink()
        return
    _write_active_payload(paths, previous_active_payload)


def _write_startup_failure_blocking_state(
    paths: SubscriptionWatchBackgroundPaths,
    *,
    run_id: str,
    pid: int,
    runner_log_path: Path | None,
) -> dict[str, Any]:
    payload = _build_active_payload(
        run_id=run_id,
        pid=pid,
        state="starting",
        reason="startup_persistence_failed",
        log_path=runner_log_path,
    )
    _write_active_payload(paths, payload)
    return payload


def _read_owned_pid(paths: SubscriptionWatchBackgroundPaths) -> int:
    if not paths.pid_path.exists():
        return 0
    return _parse_pid(paths.pid_path.read_text(encoding="utf-8").strip())


def _write_active_payload(paths: SubscriptionWatchBackgroundPaths, payload: dict[str, Any]) -> None:
    paths.active_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _normalize_terminal_payload(
    paths: SubscriptionWatchBackgroundPaths,
    payload: dict[str, Any],
    *,
    state: str,
    reason: str | None,
    run_id: Any = None,
) -> dict[str, Any]:
    normalized = dict(payload)
    normalized["state"] = state
    normalized["active"] = False
    normalized["pid"] = None
    normalized["reason"] = reason
    normalized["run_id"] = normalized.get("run_id", run_id)
    _write_active_payload(paths, normalized)
    _cleanup_owned_state(paths)
    return normalized


def reconcile_background_state(
    paths: SubscriptionWatchBackgroundPaths,
    *,
    pid_is_alive: Any = _pid_is_alive,
) -> dict[str, Any]:
    if not paths.active_path.exists():
        _cleanup_owned_state(paths)
        return {
            "state": "stopped",
            "active": False,
            "run_id": None,
            "pid": None,
            "reason": None,
        }

    try:
        raw_payload = json.loads(paths.active_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _normalize_terminal_payload(
            paths,
            {},
            state="failed",
            reason="stale_process_state",
        )

    if not isinstance(raw_payload, dict):
        return _normalize_terminal_payload(
            paths,
            {},
            state="failed",
            reason="stale_process_state",
        )

    payload = raw_payload
    state = str(payload.get("state") or "failed")
    payload_pid = _parse_pid(payload.get("pid"))
    owned_pid = _read_owned_pid(paths)
    pid_matches_owned_state = payload_pid > 0 and owned_pid == payload_pid
    startup_persistence_failed = str(payload.get("reason") or "") == "startup_persistence_failed"

    if state == "starting" and startup_persistence_failed and payload_pid > 0 and pid_is_alive(payload_pid):
        return payload

    if state in ACTIVE_PROCESS_STATES and (
        not pid_matches_owned_state or not pid_is_alive(payload_pid)
    ):
        return _normalize_terminal_payload(
            paths,
            payload,
            state="stopped" if state == "stopping" else "failed",
            reason=(str(payload.get("reason") or "operator_stop") if state == "stopping" else "stale_process_state"),
        )
    elif state in {"failed", "stopped", "completed"}:
        return _normalize_terminal_payload(
            paths,
            payload,
            state=state,
            reason=payload.get("reason"),
        )

    return payload


def _build_active_payload(
    *,
    run_id: str,
    pid: int | None,
    state: str,
    reason: str | None,
    log_path: Path | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    return {
        "state": state,
        "active": state in ACTIVE_PROCESS_STATES,
        "run_id": run_id,
        "pid": pid,
        "reason": reason,
        "runner_log_path": str(log_path) if log_path is not None else None,
        "idempotency_key": idempotency_key,
    }


def _acquire_control_lock(paths: SubscriptionWatchBackgroundPaths) -> Any | None:
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    handle = paths.lock_path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        handle.close()
        if exc.errno in {errno.EACCES, errno.EAGAIN}:
            return None
        raise
    return handle


def _release_control_lock(handle: Any) -> None:
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        handle.close()


def read_active_payload(paths: SubscriptionWatchBackgroundPaths) -> dict[str, Any] | None:
    if not paths.active_path.exists():
        return None
    payload = json.loads(paths.active_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return None
    return payload


def _read_json_file(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None


def _read_jsonl_tail(path: Path, *, limit: int) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines()[-max(limit, 0) :]:
        if not line.strip():
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _tail_lines(path: Path, *, limit: int) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()[-max(limit, 0) :]


def write_background_state(
    paths: SubscriptionWatchBackgroundPaths,
    *,
    run_id: str,
    pid: int | None,
    state: str,
    reason: str | None,
    runner_log_path: Path | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    paths.root_dir.mkdir(parents=True, exist_ok=True)
    existing_payload = read_active_payload(paths) or {}
    resolved_idempotency_key = idempotency_key
    if resolved_idempotency_key is None and existing_payload.get("run_id") == run_id:
        resolved_idempotency_key = (
            str(existing_payload.get("idempotency_key")).strip() or None
            if existing_payload.get("idempotency_key") is not None
            else None
        )
    payload = _build_active_payload(
        run_id=run_id,
        pid=pid,
        state=state,
        reason=reason,
        log_path=runner_log_path,
        idempotency_key=resolved_idempotency_key,
    )
    _write_active_payload(paths, payload)
    return payload


def write_terminal_background_state(
    paths: SubscriptionWatchBackgroundPaths,
    *,
    run_id: str,
    state: str,
    reason: str | None,
    runner_log_path: Path | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    payload = write_background_state(
        paths,
        run_id=run_id,
        pid=None,
        state=state,
        reason=reason,
        runner_log_path=runner_log_path,
        idempotency_key=idempotency_key,
    )
    _cleanup_owned_state(paths)
    return payload


class SubscriptionWatchBackgroundController:
    def __init__(
        self,
        *,
        root_dir: Path,
        python_executable: str,
        cli_module: str = "tdxquant.subscription_watch_background_runner",
        start_timeout_seconds: float = DEFAULT_START_TIMEOUT_SECONDS,
        default_stop_grace_period_seconds: int = DEFAULT_STOP_GRACE_PERIOD_SECONDS,
        stop_force_kill_timeout_seconds: float = DEFAULT_STOP_FORCE_KILL_TIMEOUT_SECONDS,
    ) -> None:
        self.paths = build_background_paths(root_dir)
        self.python_executable = python_executable
        self.cli_module = cli_module
        self.start_timeout_seconds = max(float(start_timeout_seconds), 0.0)
        self.default_stop_grace_period_seconds = max(int(default_stop_grace_period_seconds), 0)
        self.stop_force_kill_timeout_seconds = max(float(stop_force_kill_timeout_seconds), 0.0)
        self._control_lock = threading.Lock()

    def _write_active_state(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.paths.root_dir.mkdir(parents=True, exist_ok=True)
        _write_active_payload(self.paths, payload)
        return payload

    def _spawn_runner_process(
        self,
        *,
        run_id: str,
        stock_list: list[str],
        max_events: int | None,
        max_seconds: float | None,
        poll_interval: float | None,
        runner_log_path: Path,
    ) -> subprocess.Popen[str]:
        args = [
            self.python_executable,
            "-m",
            self.cli_module,
            "--root-dir",
            str(self.paths.root_dir),
            "--run-id",
            run_id,
        ]
        for stock_code in stock_list:
            args.extend(["--code", stock_code])
        if max_events is not None:
            args.extend(["--max-events", str(max_events)])
        if max_seconds is not None:
            args.extend(["--max-seconds", str(max_seconds)])
        if poll_interval is not None:
            args.extend(["--poll-interval", str(poll_interval)])
        runner_log_path.parent.mkdir(parents=True, exist_ok=True)
        runner_log_handle = runner_log_path.open("a", encoding="utf-8")
        try:
            return subprocess.Popen(
                args,
                stdout=runner_log_handle,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
            )
        finally:
            runner_log_handle.close()

    def _signal_process(self, pid: int, sig: int) -> bool:
        try:
            os.kill(pid, sig)
        except OSError:
            return False
        return True

    def _pid_is_alive(self, pid: int) -> bool:
        return _pid_is_alive(pid)

    def _wait_for_process_exit(self, pid: int, grace_period_seconds: int) -> bool:
        deadline = time.monotonic() + max(grace_period_seconds, 0)
        while self._pid_is_alive(pid):
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.05)
        return True

    def _wait_for_forced_exit(self, pid: int) -> bool:
        deadline = time.monotonic() + self.stop_force_kill_timeout_seconds
        while self._pid_is_alive(pid):
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.05)
        return True

    def _build_invalid_start_result(self, message: str) -> dict[str, Any]:
        return {
            "ok": False,
            "error": {
                "code": "INVALID_REQUEST",
                "message": message,
                "details": {},
            },
        }

    def _validate_start_request(
        self,
        *,
        stock_list: list[str],
        max_events: int | None,
        max_seconds: float | None,
        poll_interval: float | None,
    ) -> dict[str, Any] | None:
        if not stock_list:
            return self._build_invalid_start_result("subscription watch task requires at least one stock code")
        if max_events is not None and max_events <= 0:
            return self._build_invalid_start_result("subscription watch task requires max_events > 0")
        if max_seconds is not None and max_seconds <= 0:
            return self._build_invalid_start_result("subscription watch task requires max_seconds > 0")
        resolved_poll_interval = 0.25 if poll_interval is None else float(poll_interval)
        if resolved_poll_interval < 0:
            return self._build_invalid_start_result("subscription watch task requires poll_interval >= 0")
        return None

    def _current_start_result(self, payload: dict[str, Any], *, replayed: bool = False) -> dict[str, Any]:
        result = {
            "run_id": payload.get("run_id"),
            "pid": payload.get("pid"),
            "state": payload.get("state"),
            "runner_log_path": payload.get("runner_log_path"),
        }
        if replayed:
            result["replayed"] = True
        return {"ok": True, "result": result}

    def _background_state(self) -> dict[str, Any]:
        payload = reconcile_background_state(self.paths, pid_is_alive=self._pid_is_alive)
        if isinstance(payload, dict):
            return payload
        return {
            "state": "stopped",
            "active": False,
            "run_id": None,
            "pid": None,
            "reason": None,
        }

    def control_status(self) -> dict[str, Any]:
        return self._background_state()

    def _resolve_run_id(self, *, run_id: str | None = None) -> str | None:
        explicit = str(run_id).strip() if run_id is not None else None
        if explicit:
            return explicit
        current = self._background_state()
        active_run_id = str(current.get("run_id") or "").strip()
        if active_run_id and bool(current.get("active")):
            return active_run_id
        return None

    def _wait_for_startup_state(self, *, run_id: str, pid: int, runner_log_path: Path) -> dict[str, Any] | None:
        deadline = time.monotonic() + self.start_timeout_seconds
        while True:
            current = read_active_payload(self.paths) or {}
            if str(current.get("run_id") or "") == run_id:
                state = str(current.get("state") or "")
                if state == "running":
                    return current
                if state == "failed":
                    return current
                if state in {"completed", "stopped"}:
                    return current

            if not self._pid_is_alive(pid):
                current = read_active_payload(self.paths) or {}
                if str(current.get("run_id") or "") == run_id and str(current.get("state") or "") in {
                    "failed",
                    "completed",
                    "stopped",
                }:
                    return current
                return write_terminal_background_state(
                    self.paths,
                    run_id=run_id,
                    state="failed",
                    reason="start_failed",
                    runner_log_path=runner_log_path,
                )

            if time.monotonic() >= deadline:
                return None
            time.sleep(0.05)

    def _terminate_spawned_process(self, process: subprocess.Popen[str]) -> bool:
        try:
            process.terminate()
        except Exception:
            return False

        try:
            process.wait(timeout=1.0)
            return True
        except Exception:
            pass

        try:
            process.kill()
        except Exception:
            return False

        try:
            process.wait(timeout=1.0)
            return True
        except Exception:
            return False

    def start(
        self,
        *,
        stock_list: list[str],
        max_events: int | None = None,
        max_seconds: float | None = None,
        poll_interval: float | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        validation_error = self._validate_start_request(
            stock_list=stock_list,
            max_events=max_events,
            max_seconds=max_seconds,
            poll_interval=poll_interval,
        )
        if validation_error is not None:
            return validation_error
        with self._control_lock:
            control_lock = _acquire_control_lock(self.paths)
            if control_lock is None:
                return {
                    "ok": False,
                    "error": {
                        "code": "CONTROL_LOCKED",
                    },
                }
            try:
                current = reconcile_background_state(self.paths, pid_is_alive=self._pid_is_alive)
                if current.get("state") in ACTIVE_PROCESS_STATES:
                    if idempotency_key and idempotency_key == current.get("idempotency_key"):
                        return self._current_start_result(current, replayed=True)
                    return {
                        "ok": False,
                        "error": {
                            "code": "ALREADY_RUNNING",
                            "message": "subscription-watch background run is already active",
                            "details": current,
                        },
                    }

                previous_active_payload = read_active_payload(self.paths)
                run_paths = build_subscription_watch_run_paths(self.paths.root_dir)
                try:
                    process = self._spawn_runner_process(
                        run_id=run_paths.run_id,
                        stock_list=list(stock_list),
                        max_events=max_events,
                        max_seconds=max_seconds,
                        poll_interval=poll_interval,
                        runner_log_path=run_paths.runner_log_path,
                    )
                except Exception:
                    _cleanup_owned_state(self.paths)
                    raise

                try:
                    self.paths.pid_path.write_text(f"{process.pid}\n", encoding="utf-8")
                    payload = self._write_active_state(
                        _build_active_payload(
                            run_id=run_paths.run_id,
                            pid=process.pid,
                            state="starting",
                            reason=None,
                            log_path=run_paths.runner_log_path,
                            idempotency_key=idempotency_key,
                        )
                    )
                except Exception:
                    if self._terminate_spawned_process(process):
                        _cleanup_start_failure_state(
                            self.paths,
                            previous_active_payload=previous_active_payload,
                        )
                    else:
                        _write_startup_failure_blocking_state(
                            self.paths,
                            run_id=run_paths.run_id,
                            pid=process.pid,
                            runner_log_path=run_paths.runner_log_path,
                        )
                    raise
                startup_state = self._wait_for_startup_state(
                    run_id=run_paths.run_id,
                    pid=process.pid,
                    runner_log_path=run_paths.runner_log_path,
                )
                if startup_state is None:
                    return {
                        "ok": False,
                        "error": {
                            "code": "START_TIMEOUT",
                            "message": "subscription-watch background runner did not reach a stable startup state within timeout",
                            "details": payload,
                        },
                    }
                if startup_state.get("state") == "failed":
                    return {
                        "ok": False,
                        "error": {
                            "code": "START_FAILED",
                            "message": "subscription-watch background runner failed during startup",
                            "details": startup_state,
                        },
                    }
                return self._current_start_result(startup_state)
            finally:
                _release_control_lock(control_lock)

    def stop(self, *, reason: str | None = None, grace_period_seconds: int | None = None) -> dict[str, Any]:
        with self._control_lock:
            control_lock = _acquire_control_lock(self.paths)
            if control_lock is None:
                return {
                    "ok": False,
                    "error": {
                        "code": "CONTROL_LOCKED",
                    },
                }
            try:
                current = reconcile_background_state(self.paths, pid_is_alive=self._pid_is_alive)
                if current.get("state") not in ACTIVE_PROCESS_STATES:
                    return {
                        "ok": True,
                        "result": {
                            "status": "noop",
                            "reason": "NOT_RUNNING",
                            "run_id": current.get("run_id"),
                        },
                    }

                pid = _parse_pid(current.get("pid"))
                if pid <= 0:
                    return {
                        "ok": False,
                        "error": {
                            "code": "SIGNAL_FAILED",
                            "details": {"run_id": current.get("run_id"), "pid": current.get("pid")},
                        },
                    }
                stopping_payload = dict(current)
                stopping_payload["state"] = "stopping"
                stopping_payload["reason"] = reason
                stopping_payload["active"] = True
                self._write_active_state(stopping_payload)

                if not self._signal_process(pid, signal.SIGTERM):
                    if self._pid_is_alive(pid):
                        self._write_active_state(current)
                        return {
                            "ok": False,
                            "error": {
                                "code": "SIGNAL_FAILED",
                                "details": {"run_id": current.get("run_id"), "pid": pid},
                            },
                        }
                    refreshed = reconcile_background_state(self.paths, pid_is_alive=self._pid_is_alive)
                    if refreshed.get("state") in {"stopped", "failed", "completed"}:
                        return {
                            "ok": True,
                            "result": {
                                "run_id": refreshed.get("run_id"),
                                "state": refreshed.get("state"),
                            },
                        }
                    return {
                        "ok": False,
                        "error": {
                            "code": "SIGNAL_FAILED",
                            "details": {"run_id": current.get("run_id"), "pid": pid},
                        },
                    }

                resolved_grace = self.default_stop_grace_period_seconds if grace_period_seconds is None else max(
                    int(grace_period_seconds), 0
                )
                if self._wait_for_process_exit(pid, resolved_grace):
                    refreshed = reconcile_background_state(self.paths, pid_is_alive=self._pid_is_alive)
                    return {
                        "ok": True,
                        "result": {
                            "run_id": refreshed.get("run_id"),
                            "state": refreshed.get("state"),
                        },
                    }

                if not self._signal_process(pid, signal.SIGKILL) and self._pid_is_alive(pid):
                    return {
                        "ok": False,
                        "error": {
                            "code": "FORCE_SIGNAL_FAILED",
                            "details": {"run_id": current.get("run_id"), "pid": pid},
                        },
                    }
                if not self._wait_for_forced_exit(pid):
                    return {
                        "ok": False,
                        "error": {
                            "code": "FORCE_SIGNAL_FAILED",
                            "details": {"run_id": current.get("run_id"), "pid": pid},
                        },
                    }

                forced = write_terminal_background_state(
                    self.paths,
                    run_id=str(current.get("run_id") or ""),
                    state="stopped",
                    reason="forced_stop",
                    runner_log_path=Path(str(current.get("runner_log_path"))) if current.get("runner_log_path") else None,
                )
                return {
                    "ok": True,
                    "result": {
                        "run_id": forced.get("run_id"),
                        "state": forced.get("state"),
                    },
                }
            finally:
                _release_control_lock(control_lock)

    def status(
        self,
        *,
        run_id: str | None = None,
        heartbeat_stale_after_seconds: float | int | None = None,
        watermark_stale_after_seconds: float | int | None = None,
        reconnect_stale_after_seconds: float | int | None = None,
        now_utc: datetime | str | None = None,
    ) -> dict[str, Any]:
        control = self._background_state()
        resolved_run_id = self._resolve_run_id(run_id=run_id)
        watch_status = None
        if resolved_run_id is not None:
            run_paths = build_subscription_watch_run_paths(self.paths.root_dir, run_id=resolved_run_id)
            watch_status = _read_json_file(run_paths.status_path)
        return {
            "control": control,
            "watch_status": watch_status,
            "status_summary": build_subscription_watch_status_summary(
                control=control,
                watch_status=watch_status,
                heartbeat_stale_after_seconds=heartbeat_stale_after_seconds,
                watermark_stale_after_seconds=watermark_stale_after_seconds,
                reconnect_stale_after_seconds=reconnect_stale_after_seconds,
                now_utc=now_utc,
            ),
        }

    def list_runs(self) -> dict[str, Any]:
        active_payload = self._background_state()
        active = None
        last_completed = None
        last_failed = None

        active_run_id = str(active_payload.get("run_id") or "").strip()
        if active_run_id and bool(active_payload.get("active")):
            run_paths = build_subscription_watch_run_paths(self.paths.root_dir, run_id=active_run_id)
            status_payload = _read_json_file(run_paths.status_path)
            active = {
                "run_id": active_run_id,
                "control": active_payload,
                "status": status_payload,
            }

        if self.paths.root_dir.exists():
            for child in sorted(self.paths.root_dir.iterdir(), key=lambda item: item.name, reverse=True):
                if not child.is_dir():
                    continue
                run_paths = build_subscription_watch_run_paths(self.paths.root_dir, run_id=child.name)
                summary_payload = _read_json_file(run_paths.summary_path)
                if not isinstance(summary_payload, dict):
                    continue
                final_state = str(summary_payload.get("final_state") or "").strip()
                item = {
                    "run_id": child.name,
                    "summary": summary_payload,
                }
                if final_state == "completed" and last_completed is None:
                    last_completed = item
                elif final_state == "failed" and last_failed is None:
                    last_failed = item
                if last_completed is not None and last_failed is not None:
                    break

        return {
            "active": active,
            "last_completed": last_completed,
            "last_failed": last_failed,
        }

    def artifacts(self, *, run_id: str | None = None) -> dict[str, Any]:
        resolved_run_id = self._resolve_run_id(run_id=run_id)
        if resolved_run_id is None:
            raise ValueError("watch artifacts require an active or explicit run_id")
        run_paths = build_subscription_watch_run_paths(self.paths.root_dir, run_id=resolved_run_id)
        return {
            "run_id": resolved_run_id,
            "artifacts": {
                "run_dir": str(run_paths.run_dir),
                "manifest_path": str(run_paths.manifest_path),
                "status_path": str(run_paths.status_path),
                "summary_path": str(run_paths.summary_path),
                "events_jsonl_path": str(run_paths.events_jsonl_path),
                "events_csv_path": str(run_paths.events_csv_path),
                "runner_log_path": str(run_paths.runner_log_path),
            },
        }

    def events(self, *, run_id: str | None = None, tail: int = 100) -> dict[str, Any]:
        resolved_run_id = self._resolve_run_id(run_id=run_id)
        if resolved_run_id is None:
            raise ValueError("watch events require an active or explicit run_id")
        run_paths = build_subscription_watch_run_paths(self.paths.root_dir, run_id=resolved_run_id)
        return {
            "run_id": resolved_run_id,
            "events": _read_jsonl_tail(run_paths.events_jsonl_path, limit=tail),
        }

    def logs(self, *, run_id: str | None = None, tail: int = 200) -> dict[str, Any]:
        resolved_run_id = self._resolve_run_id(run_id=run_id)
        if resolved_run_id is None:
            raise ValueError("watch logs require an active or explicit run_id")
        run_paths = build_subscription_watch_run_paths(self.paths.root_dir, run_id=resolved_run_id)
        return {
            "run_id": resolved_run_id,
            "lines": _tail_lines(run_paths.runner_log_path, limit=tail),
        }
