from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from ..brokers import PingAnBrokerAdapter
from ..desktop.hid import run_hid_ping
from ..desktop.uia import (
    _click_runtime_hwnd,
    _click_runtime_target,
    _extract_dialog_text_payload_from_sources,
    _find_pingan_confirm_button,
    _find_pingan_confirm_button_win32,
    _find_pingan_result_confirm_button,
    _find_pingan_result_confirm_button_win32,
    _find_pingan_result_dialog,
    _find_pingan_result_dialog_win32,
    _safe_serialize_runtime_element,
    run_pingan_buy_fast,
    run_pingan_sell_fast,
    run_pingan_hid_submit_probe,
    run_pingan_buy_submit_once,
)
from ..models import ErrorCode, Result
from .context import (
    append_pingan_order_event,
    append_pingan_submission_ledger_entry,
    attach_trade_metadata,
    attach_trade_audit_metadata,
    attach_trade_safety_metadata,
    build_result_from_submission_ledger_row,
    capture_trade_timing,
    evaluate_trade_risk_gate,
    evaluate_trade_submission_idempotency,
    get_pingan_last_order_state_path,
    get_pingan_order_event_log_path,
    get_pingan_submission_ledger_path,
    get_pingan_trade_audit_dir,
    write_pingan_last_order_state,
    write_pingan_trade_audit,
    resolve_trade_profile,
)
from .extended_capabilities import build_pingan_desktop_extended_broker_capability_probe


def _build_trade_health_check(
    name: str,
    status: str,
    summary: str,
    *,
    detail: Any | None = None,
    critical: bool = False,
    recommended_action: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": name,
        "status": status,
        "summary": summary,
        "critical": critical,
    }
    if detail is not None:
        payload["detail"] = detail
    if recommended_action:
        payload["recommended_action"] = recommended_action
    return payload


def _summarize_trade_health_checks(checks: list[dict[str, Any]]) -> tuple[str, bool, list[str], str | None]:
    failed = [item for item in checks if item.get("status") == "failed"]
    warnings = [item for item in checks if item.get("status") == "warning"]
    if failed:
        next_action = next((str(item.get("recommended_action")) for item in failed if item.get("recommended_action")), None)
        return "failed", False, [], next_action
    if warnings:
        warning_messages = [str(item.get("summary") or item.get("name") or "warning") for item in warnings]
        next_action = next((str(item.get("recommended_action")) for item in warnings if item.get("recommended_action")), None)
        return "degraded", True, warning_messages, next_action
    return "ok", True, [], None


PINGAN_PROMOTION_GATE_STATUS_SCHEMA = "tdx.desktop_trade.pingan_promotion_gate_status.v1"
PINGAN_DESKTOP_LIFECYCLE_GATE_STATUS_SCHEMA = "tdx.desktop_trade.pingan_desktop_lifecycle_gate_status.v1"
PINGAN_TRADE_AUDIT_GATE_STATUS_SCHEMA = "tdx.desktop_trade.pingan_trade_audit_gate_status.v1"
PINGAN_LIFECYCLE_OWNER_LOCK_SCHEMA = "tdx.desktop_trade.pingan_lifecycle_owner_lock.v1"
PINGAN_LIFECYCLE_OWNER_STATE_SCHEMA = "tdx.desktop_trade.pingan_lifecycle_owner_state.v1"
PINGAN_LIFECYCLE_SUPERVISOR_SCHEMA = "tdx.desktop_trade.pingan_lifecycle_supervisor.v1"
PINGAN_REQUIRED_AUDIT_GATE_STATUSES = ("confirmed", "rejected", "failed", "exception")
PINGAN_EXCEPTION_POPUP_KEYWORDS = (
    "异常",
    "错误",
    "失败",
    "拒绝",
    "超时",
    "exception",
    "error",
    "failed",
    "timeout",
)


def _collect_dialog_text_payload_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        normalized = value.strip()
        return [normalized] if normalized else []
    if isinstance(value, dict):
        texts: list[str] = []
        for item in value.values():
            texts.extend(_collect_dialog_text_payload_strings(item))
        return texts
    if isinstance(value, (list, tuple, set)):
        texts: list[str] = []
        for item in value:
            texts.extend(_collect_dialog_text_payload_strings(item))
        return texts
    return []


def _build_pingan_exception_popup_lookup_detail(text_payload: dict[str, Any]) -> dict[str, Any]:
    passive_texts = list(dict.fromkeys(_collect_dialog_text_payload_strings(text_payload)))
    haystack = "\n".join(passive_texts).casefold()
    matched_keywords = [
        keyword for keyword in PINGAN_EXCEPTION_POPUP_KEYWORDS if keyword.casefold() in haystack
    ]
    return {
        "ok": True,
        "exception_detected": bool(matched_keywords),
        "matched_keywords": matched_keywords,
        "passive_texts": passive_texts,
        "text_payload": text_payload,
    }


def _build_pingan_broker_readiness_required_status(
    *,
    title_keyword: str,
    exe_path: str | None,
    require_broker_readiness: bool,
) -> dict[str, Any]:
    if not require_broker_readiness:
        return {
            "required": False,
            "requirement_status": "not_required",
            "broker_health_ok": None,
            "control_dispatch_executed": False,
            "order_submitted": False,
            "side_effect_level": "none",
        }
    try:
        broker_health = PingAnBrokerAdapter(title_keyword=title_keyword, exe_path=exe_path).health_check()
    except Exception as exc:
        broker_health = Result(
            ok=False,
            code=ErrorCode.EXECUTION_FAILED,
            message=f"PingAn broker readiness check failed: {exc}",
            data={"error": str(exc)},
        )
    return {
        "required": True,
        "requirement_status": "passed" if broker_health.ok else "failed",
        "requirement_reason": None if broker_health.ok else broker_health.message,
        "broker_health_ok": bool(broker_health.ok),
        "broker_health": broker_health.to_dict(),
        "control_dispatch_executed": False,
        "order_submitted": False,
        "side_effect_level": "none",
    }


def _apply_pingan_broker_readiness_required_guard(
    risk_gate: dict[str, Any],
    *,
    title_keyword: str,
    exe_path: str | None,
    require_broker_readiness: bool,
) -> dict[str, Any]:
    if not require_broker_readiness:
        return risk_gate
    status = _build_pingan_broker_readiness_required_status(
        title_keyword=title_keyword,
        exe_path=exe_path,
        require_broker_readiness=require_broker_readiness,
    )
    updated = dict(risk_gate)
    checks = list(updated.get("checks", []))
    requirement_passed = status.get("requirement_status") == "passed"
    checks.append(
        {
            "name": "broker_readiness_required",
            "passed": requirement_passed,
            "issues": [] if requirement_passed else [str(status.get("requirement_reason") or "broker readiness requirement failed")],
            "detail": status,
        }
    )
    updated["checks"] = checks
    updated["broker_readiness_required_status"] = status
    if not requirement_passed:
        updated["passed"] = False
        updated["rejection_reason"] = str(status.get("requirement_reason") or "broker readiness requirement failed")
    return updated


def _build_pingan_promotion_gate_status(
    *,
    broker_health: Result,
    detect_result: Result | None,
    risk_gate: dict[str, Any],
    idempotency: dict[str, Any],
    submission_key: str | None,
    max_price: float | None,
    lifecycle_owner_lock_status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    max_price_guard = _build_max_price_guard_status(risk_gate=risk_gate, max_price=max_price)
    submission_key_status = "provided" if submission_key else "missing"
    return {
        "schema_version": PINGAN_PROMOTION_GATE_STATUS_SCHEMA,
        "status": "partial",
        "evidence_scope": "provider_broker_ownership_and_safety_preflight",
        "execution_mode": "readonly_preflight",
        "dispatch_executed": False,
        "order_submitted": False,
        "provider_broker_ownership": {
            "status": "ready" if broker_health.ok and (detect_result is None or detect_result.ok) else "blocked",
            "broker": "pingan_desktop",
            "broker_family": "pingan",
            "adapter": "PingAnBrokerAdapter",
            "gateway_adapter": "PingAnDesktopTraderGateway",
            "manager_entrypoint": "TdxTradeManager.pingan.preflight",
            "supported_brokers": ["pingan_desktop"],
            "execution_mode": "readonly_preflight",
            "dispatch_executed": False,
            "order_submitted": False,
            "evidence": {
                "broker_health_ok": broker_health.ok,
                "buy_page_detection_ok": None if detect_result is None else detect_result.ok,
            },
            "boundary": "Read-only PingAn desktop preflight ownership evidence; no order is submitted.",
        },
        "safety_gates": {
            "status": "ready"
            if risk_gate.get("passed") and submission_key_status == "provided" and max_price is not None
            else "incomplete",
            "max_price_guard": max_price_guard,
            "submission_key": {
                "status": submission_key_status,
                "value": submission_key,
            },
            "idempotency": idempotency,
            "risk_gate": risk_gate,
            "explicit_approval": {
                "status": "not_granted",
                "required_for_live_trade": True,
                "live_trade_requires_explicit_run": True,
                "boundary": "Preflight cannot grant live trade approval; execution requires an explicit trade command.",
            },
        },
        "lifecycle_owner_lock_status": lifecycle_owner_lock_status
        or _build_pingan_preflight_lifecycle_owner_lock_status(
            lifecycle_statefile_path=None,
            lifecycle_owner_token=None,
            lifecycle_stale_after_seconds=300.0,
        ),
        "completed_gates": ["provider_broker_ownership", "safety_gates"],
        "remaining_gates": ["desktop_lifecycle", "audit_evidence", "acceptance_evidence"],
        "boundary": (
            "Partial promotion evidence only. D-07/D-08 still require desktop lifecycle, audit, "
            "and acceptance evidence before implemented status."
        ),
    }


def _build_max_price_guard_status(*, risk_gate: dict[str, Any], max_price: float | None) -> dict[str, Any]:
    requested_price = risk_gate.get("requested_price")
    if max_price is None:
        status = "missing"
        passed = False
    else:
        max_price_check = next(
            (
                check
                for check in risk_gate.get("checks", [])
                if isinstance(check, dict) and check.get("name") == "max_price"
            ),
            None,
        )
        passed = bool(max_price_check.get("passed", True)) if isinstance(max_price_check, dict) else True
        status = "configured" if passed else "failed"
    return {
        "status": status,
        "max_price": max_price,
        "requested_price": requested_price,
        "passed": passed,
    }


def _build_pingan_desktop_lifecycle_gate_status(
    *,
    checks: list[dict[str, Any]],
    dialog: str,
    require_visible: bool,
    dialog_lookup_mode: str,
    confirm_timeout: float,
    result_timeout: float,
    title_keyword: str,
    exe_path: str | None,
    observed_process_window_ownership: dict[str, Any],
    retry_policy_status: dict[str, Any],
    statefile_lock_status: dict[str, Any],
    lifecycle_control_status: dict[str, Any],
) -> dict[str, Any]:
    dialog_checks = _extract_dialog_lifecycle_checks(checks)
    exception_popup_handling_status = _build_pingan_exception_popup_handling_status(dialog_checks)
    return {
        "schema_version": PINGAN_DESKTOP_LIFECYCLE_GATE_STATUS_SCHEMA,
        "status": "partial",
        "evidence_scope": "readonly_dialog_readiness",
        "execution_mode": "readonly_dialog_readiness",
        "side_effect_level": "none",
        "order_submitted": False,
        "control_dispatch_executed": False,
        "requested": {
            "dialog": dialog,
            "require_visible": require_visible,
        },
        "dialog_lookup_mode": dialog_lookup_mode,
        "timeouts": {
            "confirm_timeout": confirm_timeout,
            "result_timeout": result_timeout,
        },
        "dialog_checks": dialog_checks,
        "declared_process_window_ownership": {
            "status": "declared",
            "title_keyword": title_keyword,
            "exe_path": exe_path,
            "boundary": "Dialog readiness records configured ownership inputs only; it does not manage the desktop process lifecycle.",
        },
        "observed_process_window_ownership": observed_process_window_ownership,
        "retry_policy_status": retry_policy_status,
        "exception_popup_handling_status": exception_popup_handling_status,
        "statefile_lock_status": statefile_lock_status,
        "lifecycle_control_status": lifecycle_control_status,
        "covered_lifecycle_gates": [
            name
            for name in (
                "confirm_lookup",
                "result_dialog_lookup",
                "result_confirm_lookup",
                "exception_popup_lookup",
            )
            if name in dialog_checks
        ],
        "remaining_lifecycle_gates": [
            "exception_popup_handling",
            "retry_policy",
            "process_window_lifecycle_ownership",
            "audit_evidence",
            "acceptance_evidence",
        ],
        "boundary": (
            "Partial desktop lifecycle evidence only. Dialog readiness performs passive lookup checks and does not "
            "submit orders, close dialogs, write artifacts, or prove exception/retry/live acceptance coverage."
        ),
    }


def _extract_dialog_lifecycle_checks(checks: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    dialog_checks: dict[str, dict[str, Any]] = {}
    for check in checks:
        name = check.get("name")
        if name not in {
            "confirm_lookup",
            "result_dialog_lookup",
            "result_confirm_lookup",
            "exception_popup_lookup",
        }:
            continue
        dialog_checks[str(name)] = {
            "status": check.get("status"),
            "summary": check.get("summary"),
            "detail": check.get("detail"),
        }
    return dialog_checks


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _read_json_object(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return payload if isinstance(payload, dict) else None


def _write_json_object(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.name}.tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp_path.replace(path)


def _resolve_pingan_lifecycle_owner_lock_status(
    *,
    statefile_path: Path,
    lock_path: Path,
    state_payload: dict[str, Any] | None,
    now: datetime,
    stale_after_seconds: float,
) -> tuple[str, bool, str | None]:
    current_owner = None
    updated_at = None
    current_status = None
    if state_payload:
        current_owner = state_payload.get("owner_token")
        current_status = str(state_payload.get("status") or "")
        updated_at = _parse_timestamp(state_payload.get("updated_at") or state_payload.get("acquired_at"))
    if updated_at is None and lock_path.exists():
        try:
            updated_at = datetime.fromtimestamp(lock_path.stat().st_mtime, tz=timezone.utc)
        except OSError:
            updated_at = None
    stale_detected = False
    if updated_at is not None and stale_after_seconds >= 0:
        stale_detected = (now - updated_at).total_seconds() > stale_after_seconds
    if stale_detected and (lock_path.exists() or current_status == "owned"):
        return "stale", True, None if current_owner is None else str(current_owner)
    if lock_path.exists() or current_status == "owned":
        return "owned", False, None if current_owner is None else str(current_owner)
    if current_status == "released":
        return "released", False, None if current_owner is None else str(current_owner)
    if statefile_path.exists():
        return "unknown", False, None if current_owner is None else str(current_owner)
    return "not_acquired", False, None if current_owner is None else str(current_owner)


def _coerce_owner_pid(value: Any) -> int | None:
    try:
        pid = int(value)
    except (TypeError, ValueError):
        return None
    return pid if pid > 0 else None


def _validate_pingan_lifecycle_owner_pid(
    state_payload: dict[str, Any] | None,
) -> tuple[int | None, bool | None, str]:
    owner_pid = _coerce_owner_pid(state_payload.get("owner_pid") if state_payload else None)
    if owner_pid is None:
        return None, None, "missing"
    try:
        os.kill(owner_pid, 0)
    except PermissionError:
        return owner_pid, True, "alive"
    except OSError:
        return owner_pid, False, "not_alive"
    return owner_pid, True, "alive"


def _build_pingan_lifecycle_owner_lock_payload(
    *,
    action: str,
    status: str,
    statefile_path: Path,
    lock_path: Path,
    owner_token: str,
    current_owner_token: str | None,
    stale_after_seconds: float,
    stale_detected: bool,
    owner_pid: int | None = None,
    owner_pid_alive: bool | None = None,
    owner_pid_status: str = "missing",
    statefile_write_executed: bool = False,
    lock_file_write_executed: bool = False,
    lock_acquired: bool = False,
    lock_released: bool = False,
    lock_file_removed: bool = False,
    stale_replaced: bool = False,
) -> dict[str, Any]:
    return {
        "schema_version": PINGAN_LIFECYCLE_OWNER_LOCK_SCHEMA,
        "action": action,
        "status": status,
        "execution_mode": "explicit_operator_lifecycle_owner_lock",
        "statefile_path": str(statefile_path),
        "lock_path": str(lock_path),
        "owner_token": owner_token,
        "current_owner_token": current_owner_token,
        "owner_pid": owner_pid,
        "owner_pid_alive": owner_pid_alive,
        "owner_pid_status": owner_pid_status,
        "pid_validation_executed": True,
        "stale_after_seconds": stale_after_seconds,
        "stale_detected": stale_detected,
        "stale_replaced": stale_replaced,
        "statefile_present": statefile_path.exists(),
        "lock_file_present": lock_path.exists(),
        "lock_acquired": lock_acquired,
        "lock_released": lock_released,
        "lock_file_write_executed": lock_file_write_executed,
        "lock_file_removed": lock_file_removed,
        "statefile_write_executed": statefile_write_executed,
        "event_log_write_executed": False,
        "submission_ledger_write_executed": False,
        "trade_audit_write_executed": False,
        "order_submitted": False,
        "control_dispatch_executed": False,
        "start_executed": False,
        "stop_executed": False,
        "restart_executed": False,
        "supervisor_owned": False,
        "backoff_executed": False,
        "process_kill_executed": False,
        "pid_ownership_claimed": False,
        "side_effect_level": "local_lifecycle_statefile" if statefile_write_executed or lock_file_write_executed or lock_file_removed else "none",
        "boundary": (
            "Local lifecycle owner lock statefile only; this operation does not start, stop, restart, "
            "kill, supervise, back off, claim desktop PID ownership, submit orders, or write trade artifacts."
        ),
    }


def _build_pingan_preflight_lifecycle_owner_lock_status(
    *,
    lifecycle_statefile_path: str | None,
    lifecycle_owner_token: str | None,
    lifecycle_stale_after_seconds: float,
    require_lifecycle_owner_lock: bool = False,
) -> dict[str, Any]:
    normalized_statefile_path = str(lifecycle_statefile_path or "").strip()
    normalized_owner_token = str(lifecycle_owner_token or "").strip()
    configured = bool(normalized_statefile_path and normalized_owner_token)
    lock_path = str(Path(f"{normalized_statefile_path}.lock")) if normalized_statefile_path else None
    summary: dict[str, Any] = {
        "schema_version": "tdx.desktop_trade.pingan_preflight_lifecycle_owner_lock_status.v1",
        "configured": configured,
        "required": bool(require_lifecycle_owner_lock),
        "status": "not_configured",
        "status_check_executed": False,
        "requirement_status": "failed" if require_lifecycle_owner_lock else "not_required",
        "requirement_reason": "lifecycle_owner_lock_not_configured" if require_lifecycle_owner_lock else None,
        "owner_token_matches": False,
        "execution_mode": "readonly_preflight",
        "statefile_path": normalized_statefile_path or None,
        "lock_path": lock_path,
        "owner_token": normalized_owner_token or None,
        "current_owner_token": None,
        "owner_pid": None,
        "owner_pid_alive": None,
        "owner_pid_status": "missing",
        "pid_validation_executed": False,
        "stale_after_seconds": float(lifecycle_stale_after_seconds),
        "stale_detected": False,
        "statefile_present": False,
        "lock_file_present": False,
        "pid_ownership_claimed": False,
        "statefile_write_executed": False,
        "lock_file_write_executed": False,
        "lock_file_removed": False,
        "order_submitted": False,
        "control_dispatch_executed": False,
        "start_executed": False,
        "stop_executed": False,
        "restart_executed": False,
        "supervisor_owned": False,
        "backoff_executed": False,
        "process_kill_executed": False,
        "side_effect_level": "none",
        "boundary": (
            "Read-only local PingAn lifecycle owner lock status for preflight; this does not acquire "
            "or release locks, start, stop, restart, kill, supervise, back off, claim real desktop PID "
            "ownership, submit orders, or write trade artifacts."
        ),
    }
    if not configured:
        return summary

    status_result = _run_pingan_lifecycle_owner_lock(
        action="status",
        statefile_path=normalized_statefile_path,
        owner_token=normalized_owner_token,
        stale_after_seconds=float(lifecycle_stale_after_seconds),
    )
    payload = status_result.data.get("lifecycle_owner_lock") if isinstance(status_result.data, dict) else None
    if not isinstance(payload, dict):
        summary.update(
            {
                "status": "status_check_failed",
                "status_check_executed": True,
                "status_result_ok": status_result.ok,
                "status_result_code": status_result.code.value if hasattr(status_result.code, "value") else str(status_result.code),
                "status_result_message": status_result.message,
            }
        )
        return summary

    summary.update(
        {
            "status": payload.get("status"),
            "status_check_executed": True,
            "status_result_ok": status_result.ok,
            "status_result_code": status_result.code.value if hasattr(status_result.code, "value") else str(status_result.code),
            "status_result_message": status_result.message,
            "statefile_path": payload.get("statefile_path"),
            "lock_path": payload.get("lock_path"),
            "owner_token": payload.get("owner_token"),
            "current_owner_token": payload.get("current_owner_token"),
            "owner_pid": payload.get("owner_pid"),
            "owner_pid_alive": payload.get("owner_pid_alive"),
            "owner_pid_status": payload.get("owner_pid_status"),
            "pid_validation_executed": payload.get("pid_validation_executed"),
            "stale_after_seconds": payload.get("stale_after_seconds"),
            "stale_detected": payload.get("stale_detected"),
            "statefile_present": payload.get("statefile_present"),
            "lock_file_present": payload.get("lock_file_present"),
            "statefile_write_executed": False,
            "lock_file_write_executed": False,
            "lock_file_removed": False,
            "order_submitted": False,
            "control_dispatch_executed": False,
            "start_executed": False,
            "stop_executed": False,
            "restart_executed": False,
            "supervisor_owned": False,
            "backoff_executed": False,
            "process_kill_executed": False,
            "pid_ownership_claimed": False,
            "side_effect_level": "none",
        }
    )
    status = str(summary.get("status") or "")
    owner_token_matches = summary.get("current_owner_token") == normalized_owner_token
    stale_detected = summary.get("stale_detected") is True
    requirement_passed = status == "owned" and owner_token_matches and not stale_detected
    if require_lifecycle_owner_lock:
        if requirement_passed:
            requirement_status = "passed"
            requirement_reason = None
        elif status != "owned":
            requirement_status = "failed"
            requirement_reason = f"lifecycle_owner_lock_status_{status or 'unknown'}"
        elif not owner_token_matches:
            requirement_status = "failed"
            requirement_reason = "lifecycle_owner_token_mismatch"
        else:
            requirement_status = "failed"
            requirement_reason = "lifecycle_owner_lock_stale"
    else:
        requirement_status = "not_required"
        requirement_reason = None
    summary.update(
        {
            "owner_token_matches": owner_token_matches,
            "requirement_status": requirement_status,
            "requirement_reason": requirement_reason,
        }
    )
    return summary


def _apply_pingan_lifecycle_owner_lock_required_guard(
    risk_gate: dict[str, Any],
    *,
    lifecycle_statefile_path: str | None,
    lifecycle_owner_token: str | None,
    lifecycle_stale_after_seconds: float,
    require_lifecycle_owner_lock: bool,
) -> dict[str, Any]:
    if not require_lifecycle_owner_lock:
        return risk_gate
    guarded = dict(risk_gate)
    guarded["checks"] = list(risk_gate.get("checks", []))
    owner_lock_status = _build_pingan_preflight_lifecycle_owner_lock_status(
        lifecycle_statefile_path=lifecycle_statefile_path,
        lifecycle_owner_token=lifecycle_owner_token,
        lifecycle_stale_after_seconds=lifecycle_stale_after_seconds,
        require_lifecycle_owner_lock=True,
    )
    requirement_passed = owner_lock_status.get("requirement_status") == "passed"
    reason = str(owner_lock_status.get("requirement_reason") or "lifecycle_owner_lock_requirement_failed")
    guarded["lifecycle_owner_lock_required_status"] = owner_lock_status
    guarded["checks"].append(
        {
            "name": "lifecycle_owner_lock_required",
            "passed": requirement_passed,
            "issues": [] if requirement_passed else [reason],
        }
    )
    if not requirement_passed:
        existing_reason = str(guarded.get("rejection_reason") or "").strip()
        guarded["passed"] = False
        guarded["rejection_reason"] = f"{existing_reason}; {reason}" if existing_reason else reason
    return guarded


def _build_pingan_lifecycle_owner_state_payload(
    *,
    status: str,
    statefile_path: Path,
    lock_path: Path,
    owner_token: str,
    now: datetime,
) -> dict[str, Any]:
    return {
        "schema_version": PINGAN_LIFECYCLE_OWNER_STATE_SCHEMA,
        "status": status,
        "broker": "pingan",
        "manager_method": "lifecycle_owner_lock",
        "owner_token": owner_token,
        "owner_pid": os.getpid(),
        "statefile_path": str(statefile_path),
        "lock_path": str(lock_path),
        "updated_at": _format_timestamp(now),
        "acquired_at": _format_timestamp(now) if status == "owned" else None,
        "released_at": _format_timestamp(now) if status == "released" else None,
    }


def _run_pingan_lifecycle_owner_lock(
    *,
    action: str,
    statefile_path: str,
    owner_token: str,
    stale_after_seconds: float = 300.0,
    force_stale: bool = False,
) -> Result:
    normalized_action = str(action or "").strip().lower()
    if normalized_action not in {"status", "acquire", "release"}:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message=f"unsupported lifecycle owner lock action: {action}")
    normalized_owner_token = str(owner_token or "").strip()
    if not normalized_owner_token:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message="owner_token is required for PingAn lifecycle owner lock")
    if not statefile_path:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message="statefile_path is required for PingAn lifecycle owner lock")

    resolved_statefile_path = Path(statefile_path)
    resolved_lock_path = Path(f"{resolved_statefile_path}.lock")
    now = _utc_now()
    state_payload = _read_json_object(resolved_statefile_path)
    owner_pid, owner_pid_alive, owner_pid_status = _validate_pingan_lifecycle_owner_pid(state_payload)
    current_status, stale_detected, current_owner = _resolve_pingan_lifecycle_owner_lock_status(
        statefile_path=resolved_statefile_path,
        lock_path=resolved_lock_path,
        state_payload=state_payload,
        now=now,
        stale_after_seconds=float(stale_after_seconds),
    )

    if normalized_action == "status":
        payload = _build_pingan_lifecycle_owner_lock_payload(
            action=normalized_action,
            status=current_status,
            statefile_path=resolved_statefile_path,
            lock_path=resolved_lock_path,
            owner_token=normalized_owner_token,
            current_owner_token=current_owner,
            owner_pid=owner_pid,
            owner_pid_alive=owner_pid_alive,
            owner_pid_status=owner_pid_status,
            stale_after_seconds=float(stale_after_seconds),
            stale_detected=stale_detected,
        )
        return Result(ok=True, code=ErrorCode.OK, message="completed PingAn lifecycle owner lock status check", data={"lifecycle_owner_lock": payload})

    if normalized_action == "acquire":
        if current_status == "owned" and current_owner != normalized_owner_token:
            payload = _build_pingan_lifecycle_owner_lock_payload(
                action=normalized_action,
                status="blocked_by_active_lock",
                statefile_path=resolved_statefile_path,
                lock_path=resolved_lock_path,
                owner_token=normalized_owner_token,
                current_owner_token=current_owner,
                owner_pid=owner_pid,
                owner_pid_alive=owner_pid_alive,
                owner_pid_status=owner_pid_status,
                stale_after_seconds=float(stale_after_seconds),
                stale_detected=stale_detected,
            )
            return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message="PingAn lifecycle owner lock is held by another owner", data={"lifecycle_owner_lock": payload})
        stale_replaced = False
        if current_status == "stale":
            if not force_stale:
                payload = _build_pingan_lifecycle_owner_lock_payload(
                    action=normalized_action,
                    status="stale_requires_force",
                    statefile_path=resolved_statefile_path,
                    lock_path=resolved_lock_path,
                    owner_token=normalized_owner_token,
                    current_owner_token=current_owner,
                    owner_pid=owner_pid,
                    owner_pid_alive=owner_pid_alive,
                    owner_pid_status=owner_pid_status,
                    stale_after_seconds=float(stale_after_seconds),
                    stale_detected=True,
                )
                return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message="PingAn lifecycle owner lock is stale; pass force_stale to replace it", data={"lifecycle_owner_lock": payload})
            try:
                resolved_lock_path.unlink()
            except FileNotFoundError:
                pass
            stale_replaced = True
        resolved_statefile_path.parent.mkdir(parents=True, exist_ok=True)
        lock_payload = {
            "schema_version": PINGAN_LIFECYCLE_OWNER_LOCK_SCHEMA,
            "owner_token": normalized_owner_token,
            "statefile_path": str(resolved_statefile_path),
            "created_at": _format_timestamp(now),
            "owner_pid": os.getpid(),
        }
        try:
            with resolved_lock_path.open("x", encoding="utf-8") as handle:
                json.dump(lock_payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
                handle.write("\n")
        except FileExistsError:
            payload = _build_pingan_lifecycle_owner_lock_payload(
                action=normalized_action,
                status="blocked_by_active_lock",
                statefile_path=resolved_statefile_path,
                lock_path=resolved_lock_path,
                owner_token=normalized_owner_token,
                current_owner_token=current_owner,
                owner_pid=owner_pid,
                owner_pid_alive=owner_pid_alive,
                owner_pid_status=owner_pid_status,
                stale_after_seconds=float(stale_after_seconds),
                stale_detected=stale_detected,
            )
            return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message="PingAn lifecycle owner lock file already exists", data={"lifecycle_owner_lock": payload})
        state_payload = _build_pingan_lifecycle_owner_state_payload(
            status="owned",
            statefile_path=resolved_statefile_path,
            lock_path=resolved_lock_path,
            owner_token=normalized_owner_token,
            now=now,
        )
        _write_json_object(resolved_statefile_path, state_payload)
        payload = _build_pingan_lifecycle_owner_lock_payload(
            action=normalized_action,
            status="owned",
            statefile_path=resolved_statefile_path,
            lock_path=resolved_lock_path,
            owner_token=normalized_owner_token,
            current_owner_token=normalized_owner_token,
            owner_pid=os.getpid(),
            owner_pid_alive=True,
            owner_pid_status="alive",
            stale_after_seconds=float(stale_after_seconds),
            stale_detected=stale_detected,
            statefile_write_executed=True,
            lock_file_write_executed=True,
            lock_acquired=True,
            stale_replaced=stale_replaced,
        )
        return Result(ok=True, code=ErrorCode.OK, message="acquired PingAn lifecycle owner lock", data={"lifecycle_owner_lock": payload})

    if current_owner is not None and current_owner != normalized_owner_token:
        payload = _build_pingan_lifecycle_owner_lock_payload(
            action=normalized_action,
            status="owner_token_mismatch",
            statefile_path=resolved_statefile_path,
            lock_path=resolved_lock_path,
            owner_token=normalized_owner_token,
            current_owner_token=current_owner,
            owner_pid=owner_pid,
            owner_pid_alive=owner_pid_alive,
            owner_pid_status=owner_pid_status,
            stale_after_seconds=float(stale_after_seconds),
            stale_detected=stale_detected,
        )
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message="PingAn lifecycle owner lock release requires the recorded owner token", data={"lifecycle_owner_lock": payload})
    lock_file_removed = False
    try:
        resolved_lock_path.unlink()
        lock_file_removed = True
    except FileNotFoundError:
        pass
    released_payload = _build_pingan_lifecycle_owner_state_payload(
        status="released",
        statefile_path=resolved_statefile_path,
        lock_path=resolved_lock_path,
        owner_token=normalized_owner_token,
        now=now,
    )
    _write_json_object(resolved_statefile_path, released_payload)
    payload = _build_pingan_lifecycle_owner_lock_payload(
        action=normalized_action,
        status="released",
        statefile_path=resolved_statefile_path,
        lock_path=resolved_lock_path,
        owner_token=normalized_owner_token,
        current_owner_token=normalized_owner_token,
        owner_pid=os.getpid(),
        owner_pid_alive=True,
        owner_pid_status="alive",
        stale_after_seconds=float(stale_after_seconds),
        stale_detected=stale_detected,
        statefile_write_executed=True,
        lock_released=True,
        lock_file_removed=lock_file_removed,
    )
    return Result(ok=True, code=ErrorCode.OK, message="released PingAn lifecycle owner lock", data={"lifecycle_owner_lock": payload})


def _coerce_non_negative_int(value: Any, *, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= 0 else default


def _run_pingan_lifecycle_supervisor_tick(
    *,
    statefile_path: str,
    owner_token: str,
    title_keyword: str,
    exe_path: str | None,
    stale_after_seconds: float = 300.0,
    max_restart_attempts: int = 1,
    backoff_seconds: float = 30.0,
) -> Result:
    normalized_owner_token = str(owner_token or "").strip()
    if not normalized_owner_token:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message="owner_token is required for PingAn lifecycle supervisor control")
    if not statefile_path:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message="statefile_path is required for PingAn lifecycle supervisor control")

    resolved_statefile_path = Path(statefile_path)
    resolved_lock_path = Path(f"{resolved_statefile_path}.lock")
    normalized_max_restart_attempts = _coerce_non_negative_int(max_restart_attempts, default=1)
    normalized_backoff_seconds = max(0.0, float(backoff_seconds))
    now = _utc_now()
    status_result = _run_pingan_lifecycle_owner_lock(
        action="status",
        statefile_path=str(resolved_statefile_path),
        owner_token=normalized_owner_token,
        stale_after_seconds=float(stale_after_seconds),
    )
    owner_payload = status_result.data.get("lifecycle_owner_lock") if isinstance(status_result.data, dict) else None
    owner_status = str(owner_payload.get("status") or "status_check_failed") if isinstance(owner_payload, dict) else "status_check_failed"
    owner_token_matches = bool(
        isinstance(owner_payload, dict) and owner_payload.get("current_owner_token") == normalized_owner_token
    )
    owner_pid_alive = owner_payload.get("owner_pid_alive") if isinstance(owner_payload, dict) else None
    stale_detected = bool(owner_payload.get("stale_detected")) if isinstance(owner_payload, dict) else False
    supervisor_owned = (
        status_result.ok
        and owner_status == "owned"
        and owner_token_matches
        and not stale_detected
        and owner_pid_alive is True
    )

    if not supervisor_owned:
        if owner_status != "owned":
            status = "owner_lock_not_owned"
        elif not owner_token_matches:
            status = "owner_token_mismatch"
        elif stale_detected:
            status = "owner_lock_stale"
        else:
            status = "owner_pid_not_alive"
        payload = {
            "schema_version": PINGAN_LIFECYCLE_SUPERVISOR_SCHEMA,
            "action": "tick",
            "status": status,
            "execution_mode": "explicit_operator_lifecycle_supervisor_control",
            "statefile_path": str(resolved_statefile_path),
            "lock_path": str(resolved_lock_path),
            "owner_token": normalized_owner_token,
            "current_owner_token": owner_payload.get("current_owner_token") if isinstance(owner_payload, dict) else None,
            "owner_lock_status": owner_payload,
            "owner_token_matches": owner_token_matches,
            "owner_pid_alive": owner_pid_alive,
            "owner_pid_status": owner_payload.get("owner_pid_status") if isinstance(owner_payload, dict) else "missing",
            "stale_after_seconds": float(stale_after_seconds),
            "stale_detected": stale_detected,
            "supervisor_owned": False,
            "broker_health_ok": None,
            "control_dispatch_executed": False,
            "statefile_write_executed": False,
            "restart_executed": False,
            "backoff_executed": False,
            "restart_attempt_count": 0,
            "max_restart_attempts": normalized_max_restart_attempts,
            "backoff_seconds": normalized_backoff_seconds,
            "last_restart_attempt_at": None,
            "next_allowed_restart_at": None,
            "order_submitted": False,
            "process_kill_executed": False,
            "pid_ownership_claimed": False,
            "side_effect_level": "none",
            "boundary": (
                "Explicit local PingAn lifecycle supervisor tick requires an owned lifecycle statefile; "
                "this rejected tick does not observe broker health, write lifecycle state, submit orders, "
                "execute workflows, kill/start processes, or claim real desktop PID ownership."
            ),
        }
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message="PingAn lifecycle supervisor requires an owned lifecycle owner lock",
            data={"lifecycle_supervisor": payload},
        )

    broker_health = PingAnBrokerAdapter(title_keyword=title_keyword, exe_path=exe_path).health_check()
    broker_health_ok = bool(broker_health.ok)
    state_payload = _read_json_object(resolved_statefile_path) or {}
    previous_supervisor = state_payload.get("supervisor") if isinstance(state_payload.get("supervisor"), dict) else {}
    restart_attempt_count = _coerce_non_negative_int(previous_supervisor.get("restart_attempt_count"), default=0)
    previous_last_restart_at = _parse_timestamp(previous_supervisor.get("last_restart_attempt_at"))
    last_restart_at = previous_last_restart_at
    restart_executed = False
    backoff_executed = False
    next_allowed_restart_at: datetime | None = None

    if broker_health_ok:
        status = "healthy"
        restart_attempt_count = 0
        last_restart_at = None
    else:
        if previous_last_restart_at is not None and normalized_backoff_seconds > 0:
            next_allowed_restart_at = previous_last_restart_at + timedelta(seconds=normalized_backoff_seconds)
        inside_backoff = (
            next_allowed_restart_at is not None
            and now < next_allowed_restart_at
        )
        if inside_backoff:
            status = "backoff_waiting"
            backoff_executed = True
        elif restart_attempt_count >= normalized_max_restart_attempts:
            status = "max_restart_attempts_reached"
        else:
            status = "restart_recorded"
            restart_attempt_count += 1
            restart_executed = True
            last_restart_at = now
            if normalized_backoff_seconds > 0:
                next_allowed_restart_at = now + timedelta(seconds=normalized_backoff_seconds)

    supervisor_state = {
        "schema_version": PINGAN_LIFECYCLE_SUPERVISOR_SCHEMA,
        "status": status,
        "execution_mode": "explicit_operator_lifecycle_supervisor_control",
        "updated_at": _format_timestamp(now),
        "owner_token": normalized_owner_token,
        "broker_health_ok": broker_health_ok,
        "broker_health_message": broker_health.message,
        "broker_health_code": broker_health.code.value if hasattr(broker_health.code, "value") else str(broker_health.code),
        "control_dispatch_executed": True,
        "restart_executed": restart_executed,
        "backoff_executed": backoff_executed,
        "restart_attempt_count": restart_attempt_count,
        "max_restart_attempts": normalized_max_restart_attempts,
        "backoff_seconds": normalized_backoff_seconds,
        "last_restart_attempt_at": _format_timestamp(last_restart_at) if last_restart_at is not None else None,
        "next_allowed_restart_at": _format_timestamp(next_allowed_restart_at) if next_allowed_restart_at is not None else None,
        "order_submitted": False,
        "process_kill_executed": False,
        "pid_ownership_claimed": False,
        "side_effect_level": "local_lifecycle_statefile",
    }
    updated_state = dict(state_payload)
    updated_state.update(
        {
            "status": "owned",
            "broker": "pingan",
            "owner_token": normalized_owner_token,
            "owner_pid": os.getpid(),
            "statefile_path": str(resolved_statefile_path),
            "lock_path": str(resolved_lock_path),
            "updated_at": _format_timestamp(now),
            "supervisor": supervisor_state,
        }
    )
    _write_json_object(resolved_statefile_path, updated_state)

    payload = {
        **supervisor_state,
        "action": "tick",
        "statefile_path": str(resolved_statefile_path),
        "lock_path": str(resolved_lock_path),
        "current_owner_token": normalized_owner_token,
        "owner_lock_status": owner_payload,
        "owner_token_matches": True,
        "owner_pid_alive": owner_pid_alive,
        "owner_pid_status": owner_payload.get("owner_pid_status") if isinstance(owner_payload, dict) else "missing",
        "stale_after_seconds": float(stale_after_seconds),
        "stale_detected": False,
        "supervisor_owned": True,
        "statefile_write_executed": True,
        "boundary": (
            "Local statefile-backed lifecycle control only: records PingAn broker health, restart, "
            "and backoff decisions under an explicit owner lock; it does not submit orders, execute "
            "catalog/task/report/bundle workflows, kill/start the real PingAn process, or claim real "
            "desktop PID ownership."
        ),
    }
    return Result(
        ok=True,
        code=ErrorCode.OK,
        message=f"completed PingAn lifecycle supervisor tick: {status}",
        data={"lifecycle_supervisor": payload},
    )


def _run_pingan_lifecycle_supervisor_run(
    *,
    statefile_path: str,
    owner_token: str,
    title_keyword: str,
    exe_path: str | None,
    stale_after_seconds: float = 300.0,
    max_restart_attempts: int = 1,
    backoff_seconds: float = 30.0,
    max_ticks: int = 1,
    interval_seconds: float = 0.0,
) -> Result:
    normalized_max_ticks = _coerce_non_negative_int(max_ticks, default=1)
    if normalized_max_ticks < 1:
        return Result(ok=False, code=ErrorCode.INVALID_REQUEST, message="max_ticks must be at least 1 for PingAn lifecycle supervisor run")
    normalized_interval_seconds = max(0.0, float(interval_seconds))
    ticks: list[dict[str, Any]] = []
    all_ok = True
    for index in range(normalized_max_ticks):
        tick_result = _run_pingan_lifecycle_supervisor_tick(
            statefile_path=statefile_path,
            owner_token=owner_token,
            title_keyword=title_keyword,
            exe_path=exe_path,
            stale_after_seconds=stale_after_seconds,
            max_restart_attempts=max_restart_attempts,
            backoff_seconds=backoff_seconds,
        )
        tick_payload = tick_result.data.get("lifecycle_supervisor") if isinstance(tick_result.data, dict) else None
        if isinstance(tick_payload, dict):
            ticks.append(tick_payload)
        else:
            ticks.append({"status": "missing_tick_payload", "ok": tick_result.ok, "message": tick_result.message})
        if not tick_result.ok:
            all_ok = False
            break
        if normalized_interval_seconds > 0 and index + 1 < normalized_max_ticks:
            time.sleep(normalized_interval_seconds)

    run_payload = {
        "schema_version": PINGAN_LIFECYCLE_SUPERVISOR_SCHEMA,
        "action": "run",
        "status": "completed" if all_ok and len(ticks) == normalized_max_ticks else "stopped",
        "execution_mode": "explicit_operator_lifecycle_supervisor_control",
        "statefile_path": statefile_path,
        "owner_token": owner_token,
        "tick_count": len(ticks),
        "max_ticks": normalized_max_ticks,
        "interval_seconds": normalized_interval_seconds,
        "ticks": ticks,
        "order_submitted": False,
        "process_kill_executed": False,
        "pid_ownership_claimed": False,
        "boundary": (
            "Bounded foreground PingAn lifecycle supervisor run only; each tick is local statefile-backed "
            "lifecycle control and does not submit orders, execute workflows, kill/start processes, or "
            "claim real desktop PID ownership."
        ),
    }
    return Result(
        ok=all_ok,
        code=ErrorCode.OK if all_ok else ErrorCode.INVALID_REQUEST,
        message=f"completed PingAn lifecycle supervisor run with {len(ticks)} tick(s)",
        data={"lifecycle_supervisor_run": run_payload},
    )


def _build_pingan_lifecycle_control_status(*, title_keyword: str, exe_path: str | None) -> dict[str, Any]:
    return {
        "status": "not_owned",
        "execution_mode": "readonly_lifecycle_control_status",
        "control_available": False,
        "title_keyword": title_keyword,
        "exe_path": exe_path,
        "start_executed": False,
        "stop_executed": False,
        "restart_executed": False,
        "supervisor_owned": False,
        "backoff_executed": False,
        "process_kill_executed": False,
        "pid_ownership_claimed": False,
        "owner_token_written": False,
        "side_effect_level": "none",
        "boundary": (
            "Read-only lifecycle control status only; dialog readiness does not start, stop, "
            "restart, kill, supervise, back off, claim PID ownership, or write owner tokens."
        ),
    }


def _build_pingan_statefile_lock_status(artifact_targets: dict[str, str]) -> dict[str, Any]:
    return {
        "status": "not_acquired",
        "execution_mode": "readonly_lock_status",
        "artifact_targets": dict(artifact_targets),
        "lock_acquired": False,
        "owner_token": None,
        "statefile_write_executed": False,
        "event_log_write_executed": False,
        "submission_ledger_write_executed": False,
        "trade_audit_write_executed": False,
        "side_effect_level": "none",
        "boundary": (
            "Read-only statefile lock status only; dialog readiness does not acquire locks, "
            "write owner tokens, write trade artifacts, or own the desktop process lifecycle."
        ),
    }


def _build_pingan_exception_popup_handling_status(
    dialog_checks: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    lookup = dialog_checks.get("exception_popup_lookup", {})
    detail = lookup.get("detail") if isinstance(lookup.get("detail"), dict) else {}
    exception_detected = detail.get("exception_detected")
    matched_keywords = detail.get("matched_keywords") if isinstance(detail.get("matched_keywords"), list) else []
    if exception_detected is True:
        status = "manual_required"
    elif exception_detected is False:
        status = "not_triggered"
    else:
        status = "unknown"
    return {
        "status": status,
        "execution_mode": "readonly_handling_status",
        "handling_available": False,
        "lookup_status": lookup.get("status"),
        "lookup_summary": lookup.get("summary"),
        "exception_detected": exception_detected,
        "matched_keywords": matched_keywords,
        "manual_action_required": exception_detected is True,
        "close_executed": False,
        "confirm_click_executed": False,
        "recovery_executed": False,
        "retry_executed": False,
        "resubmission_executed": False,
        "side_effect_level": "none",
        "boundary": (
            "Read-only exception popup handling status only; dialog readiness does not close popups, "
            "click controls, recover, retry, resubmit, or write trade artifacts."
        ),
    }


def _build_pingan_retry_policy_status(profile_options: dict[str, Any]) -> dict[str, Any]:
    configured_policy = {
        key: profile_options[key]
        for key in ("retry_attempts", "retry_backoff_seconds", "retry_backoff_mode")
        if key in profile_options
    }
    return {
        "status": "configured" if configured_policy else "not_configured",
        "execution_mode": "readonly_policy_status",
        "policy_source": "trade_profile",
        "configured_policy": configured_policy,
        "retry_executed": False,
        "backoff_executed": False,
        "recovery_executed": False,
        "resubmission_executed": False,
        "side_effect_level": "none",
        "boundary": (
            "Read-only retry policy status only; dialog readiness does not retry, back off, "
            "recover, resubmit, or write trade artifacts."
        ),
    }


def _build_pingan_observed_process_window_ownership(
    *,
    health_result: Result,
    title_keyword: str,
    exe_path: str | None,
) -> dict[str, Any]:
    health_data = health_result.data if isinstance(health_result.data, dict) else {}
    runtime = health_data.get("runtime") if isinstance(health_data.get("runtime"), dict) else {}
    window = health_data.get("window") if isinstance(health_data.get("window"), dict) else {}
    runtime_ok = runtime.get("ok") if isinstance(runtime, dict) else None
    window_ok = window.get("ok") if isinstance(window, dict) else None
    return {
        "status": "observed" if health_result.ok else "unverified",
        "title_keyword": title_keyword,
        "exe_path": exe_path,
        "runtime_ok": runtime_ok,
        "window_ok": window_ok,
        "health_result": health_result.to_dict(),
        "side_effect_level": "none",
        "boundary": (
            "Read-only runtime/window observation only; dialog readiness does not start, stop, "
            "restart, supervise, lock, or own the PingAn desktop process."
        ),
    }


def _build_pingan_unverified_process_window_ownership(
    *,
    title_keyword: str,
    exe_path: str | None,
    error: Exception,
) -> dict[str, Any]:
    return {
        "status": "unverified",
        "title_keyword": title_keyword,
        "exe_path": exe_path,
        "runtime_ok": None,
        "window_ok": None,
        "health_result": {
            "ok": False,
            "code": ErrorCode.EXECUTION_FAILED.value,
            "message": "process/window observation failed",
            "data": {},
            "warnings": [],
            "next_action": None,
            "last_error": str(error),
        },
        "side_effect_level": "none",
        "boundary": (
            "Read-only runtime/window observation only; dialog readiness does not start, stop, "
            "restart, supervise, lock, or own the PingAn desktop process."
        ),
    }


def _build_pingan_audit_status_classification(result: Result, covered_status: str) -> dict[str, Any]:
    data = result.data if isinstance(result.data, dict) else {}
    trade_safety = data.get("trade_safety", {})
    trade_safety = trade_safety if isinstance(trade_safety, dict) else {}
    risk_gate = trade_safety.get("risk_gate", {})
    risk_gate = risk_gate if isinstance(risk_gate, dict) else {}
    idempotency = trade_safety.get("idempotency", {})
    idempotency = idempotency if isinstance(idempotency, dict) else {}
    idempotency_decision = str(idempotency.get("decision") or "unknown")
    explicit_exception = isinstance(data.get("desktop_exception"), dict) or isinstance(data.get("trade_exception"), dict)
    rejected_request = (
        idempotency_decision == "reject_conflict"
        or not bool(risk_gate.get("passed", True))
        or result.code == ErrorCode.INVALID_REQUEST
    )

    if idempotency_decision == "skip_duplicate":
        source = "duplicate_submission_key_skip"
    elif rejected_request:
        source = "rejected_request"
    elif explicit_exception:
        source = "explicit_exception_metadata"
    elif result.ok:
        source = "confirmed_result"
    else:
        source = "generic_execution_failure"

    return {
        "status": covered_status,
        "source": source,
        "result_ok": bool(result.ok),
        "error_code": result.code.value if isinstance(result.code, ErrorCode) else str(result.code),
        "idempotency_decision": idempotency_decision,
        "rejected_request": rejected_request,
        "explicit_exception_metadata": explicit_exception,
        "boundary": (
            "Audit-only status classification for one finalized PingAn result; does not implement retry, "
            "recovery, broker readiness, or live/manual acceptance."
        ),
    }


def _build_pingan_trade_audit_gate_status(result: Result) -> dict[str, Any]:
    trade_audit = result.data.get("trade_audit", {})
    trade_audit = trade_audit if isinstance(trade_audit, dict) else {}
    artifacts = result.data.get("artifacts", {})
    artifacts = artifacts if isinstance(artifacts, dict) else {}
    covered_status = str(trade_audit.get("status") or "unknown")
    artifact_paths = {
        "last_order_state_path": artifacts.get("last_order_state_path"),
        "order_event_log_path": artifacts.get("order_event_log_path"),
        "submission_ledger_path": artifacts.get("submission_ledger_path"),
        "trade_audit_path": artifacts.get("trade_audit_path"),
    }
    return {
        "schema_version": PINGAN_TRADE_AUDIT_GATE_STATUS_SCHEMA,
        "status": "partial",
        "evidence_scope": "single_finalized_trade_result",
        "audit_id": trade_audit.get("audit_id"),
        "covered_audit_status": covered_status,
        "audit_status_classification": _build_pingan_audit_status_classification(result, covered_status),
        "broker": trade_audit.get("broker"),
        "method": trade_audit.get("method"),
        "artifact_paths": artifact_paths,
        "persisted_artifacts": {
            "last_order_state": bool(artifact_paths["last_order_state_path"]),
            "order_event_log": bool(artifact_paths["order_event_log_path"]),
            "submission_ledger": bool(artifact_paths["submission_ledger_path"]),
            "trade_audit": bool(artifact_paths["trade_audit_path"]),
        },
        "remaining_audit_gate_statuses": [
            status for status in PINGAN_REQUIRED_AUDIT_GATE_STATUSES if status != covered_status
        ],
        "boundary": (
            "Partial audit promotion evidence for one finalized result only. Separate success, failure, "
            "rejection, exception, and acceptance evidence are still required before implemented status."
        ),
    }


def _serialize_dialog_lookup_target(target: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": bool(target.get("ok")),
    }
    if "lookup_mode" in target:
        payload["lookup_mode"] = target.get("lookup_mode")
    if "lookup_fallback_from" in target:
        payload["lookup_fallback_from"] = target.get("lookup_fallback_from")
    if "last_error" in target:
        payload["last_error"] = target.get("last_error")
    if target.get("hwnd") is not None:
        payload["hwnd"] = target.get("hwnd")
    info = target.get("info")
    if info is not None:
        payload["info"] = {
            "handle": getattr(info, "handle", None),
            "name": getattr(info, "name", None),
            "class_name": getattr(info, "class_name", None),
            "automation_id": getattr(info, "automation_id", None),
            "control_type": getattr(info, "control_type", None),
        }
    return payload


def _resolve_dialog_check_status(*, found: bool, require_visible: bool) -> str:
    if found:
        return "ok"
    return "failed" if require_visible else "warning"


def _find_confirm_target_for_lookup(title_keyword: str, lookup_mode: str, timeout: float) -> dict[str, Any]:
    if lookup_mode == "win32_experimental":
        experimental = _find_pingan_confirm_button_win32(timeout=timeout)
        if experimental["ok"]:
            experimental["lookup_mode"] = "win32_experimental"
            return experimental
        fallback = _find_pingan_confirm_button(title_keyword=title_keyword, timeout=timeout)
        fallback["lookup_mode"] = "uia_fallback"
        fallback["lookup_fallback_from"] = experimental.get("last_error")
        return fallback
    target = _find_pingan_confirm_button(title_keyword=title_keyword, timeout=timeout)
    target["lookup_mode"] = "uia"
    return target


def _find_result_dialog_for_lookup(title_keyword: str, lookup_mode: str, timeout: float) -> dict[str, Any]:
    if lookup_mode == "win32_experimental":
        experimental = _find_pingan_result_dialog_win32(timeout=timeout)
        if experimental["ok"]:
            experimental["lookup_mode"] = "win32_experimental"
            return experimental
        fallback = _find_pingan_result_dialog(title_keyword=title_keyword, timeout=timeout)
        fallback["lookup_mode"] = "uia_fallback"
        fallback["lookup_fallback_from"] = experimental.get("last_error")
        return fallback
    target = _find_pingan_result_dialog(title_keyword=title_keyword, timeout=timeout)
    target["lookup_mode"] = "uia"
    return target


def _find_result_confirm_target_for_lookup(title_keyword: str, lookup_mode: str, timeout: float) -> dict[str, Any]:
    if lookup_mode == "win32_experimental":
        experimental = _find_pingan_result_confirm_button_win32(timeout=timeout)
        if experimental["ok"]:
            experimental["lookup_mode"] = "win32_experimental"
            return experimental
        fallback = _find_pingan_result_confirm_button(title_keyword=title_keyword, timeout=timeout)
        fallback["lookup_mode"] = "uia_fallback"
        fallback["lookup_fallback_from"] = experimental.get("last_error")
        return fallback
    target = _find_pingan_result_confirm_button(title_keyword=title_keyword, timeout=timeout)
    target["lookup_mode"] = "uia"
    return target


def _click_lookup_target(target: dict[str, Any], *, post_delay: float) -> Result:
    if target.get("hwnd") is not None:
        return _click_runtime_hwnd(int(target["hwnd"]), strategy="wm_command", post_delay=post_delay)
    return _click_runtime_target(target, strategy="wm_command", post_delay=post_delay)


class _PingAnTradeProxy:
    __slots__ = ("_manager",)

    def __init__(self, manager: "TdxTradeManager") -> None:
        self._manager = manager

    def extended_broker_capabilities(self, *, generated_at: str | None = None) -> Result:
        effective_profile = self._manager._build_effective_profile({})

        def run() -> Result:
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="completed PingAn desktop extended broker capability probe",
                data={
                    "broker_capabilities": build_pingan_desktop_extended_broker_capability_probe(
                        generated_at=generated_at
                    )
                },
            )

        result, timing = capture_trade_timing("pingan.extended_broker_capabilities", run)
        attach_trade_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            broker="pingan",
            method="extended_broker_capabilities",
            title_keyword=self._manager.title_keyword,
            exe_path=self._manager.exe_path,
            timing=timing,
        )
        return result

    def lifecycle_owner_lock(
        self,
        *,
        action: str,
        statefile_path: str,
        owner_token: str,
        stale_after_seconds: float = 300.0,
        force_stale: bool = False,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})

        def run() -> Result:
            return _run_pingan_lifecycle_owner_lock(
                action=action,
                statefile_path=statefile_path,
                owner_token=owner_token,
                stale_after_seconds=stale_after_seconds,
                force_stale=force_stale,
            )

        result, timing = capture_trade_timing("pingan.lifecycle_owner_lock", run)
        attach_trade_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            broker="pingan",
            method="lifecycle_owner_lock",
            title_keyword=self._manager.title_keyword,
            exe_path=self._manager.exe_path,
            timing=timing,
        )
        return result

    def lifecycle_supervisor_tick(
        self,
        *,
        statefile_path: str,
        owner_token: str,
        stale_after_seconds: float = 300.0,
        max_restart_attempts: int = 1,
        backoff_seconds: float = 30.0,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})

        def run() -> Result:
            return _run_pingan_lifecycle_supervisor_tick(
                statefile_path=statefile_path,
                owner_token=owner_token,
                title_keyword=self._manager.title_keyword,
                exe_path=self._manager.exe_path,
                stale_after_seconds=stale_after_seconds,
                max_restart_attempts=max_restart_attempts,
                backoff_seconds=backoff_seconds,
            )

        result, timing = capture_trade_timing("pingan.lifecycle_supervisor_tick", run)
        attach_trade_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            broker="pingan",
            method="lifecycle_supervisor_tick",
            title_keyword=self._manager.title_keyword,
            exe_path=self._manager.exe_path,
            timing=timing,
        )
        return result

    def lifecycle_supervisor_run(
        self,
        *,
        statefile_path: str,
        owner_token: str,
        stale_after_seconds: float = 300.0,
        max_restart_attempts: int = 1,
        backoff_seconds: float = 30.0,
        max_ticks: int = 1,
        interval_seconds: float = 0.0,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})

        def run() -> Result:
            return _run_pingan_lifecycle_supervisor_run(
                statefile_path=statefile_path,
                owner_token=owner_token,
                title_keyword=self._manager.title_keyword,
                exe_path=self._manager.exe_path,
                stale_after_seconds=stale_after_seconds,
                max_restart_attempts=max_restart_attempts,
                backoff_seconds=backoff_seconds,
                max_ticks=max_ticks,
                interval_seconds=interval_seconds,
            )

        result, timing = capture_trade_timing("pingan.lifecycle_supervisor_run", run)
        attach_trade_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            broker="pingan",
            method="lifecycle_supervisor_run",
            title_keyword=self._manager.title_keyword,
            exe_path=self._manager.exe_path,
            timing=timing,
        )
        return result

    def buy(
        self,
        *,
        port: str,
        code: str,
        price: str,
        quantity: int,
        baudrate: int = 115200,
        timeout: float = 2.0,
        max_depth: int = 12,
        close_result_dialog: bool = True,
        submission_key: str | None = None,
        max_price: float | None = None,
        lifecycle_statefile_path: str | None = None,
        lifecycle_owner_token: str | None = None,
        lifecycle_stale_after_seconds: float = 300.0,
        require_lifecycle_owner_lock: bool = False,
        require_broker_readiness: bool = False,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        idempotency = self._manager._evaluate_idempotency(
            broker="pingan",
            method="buy",
            code=code,
            price=price,
            quantity=quantity,
            submission_key=submission_key,
        )
        if idempotency["decision"] == "skip_duplicate":
            result = self._manager._build_duplicate_submission_result(prior_row=idempotency["prior_row"])
            return self._manager._finalize_result(
                result,
                broker="pingan",
                method="buy",
                profile_options=effective_profile,
                timing={},
                submission_key=submission_key,
                risk_gate={"passed": True, "checks": [], "requested_price": None, "max_price": max_price, "rejection_reason": None},
                idempotency=idempotency,
                request_context={"code": code, "price": price, "quantity": quantity},
            )
        if idempotency["decision"] == "reject_conflict":
            result = self._manager._build_submission_key_conflict_result(
                code=code,
                price=price,
                quantity=quantity,
                idempotency=idempotency,
            )
            return self._manager._finalize_result(
                result,
                broker="pingan",
                method="buy",
                profile_options=effective_profile,
                timing={},
                submission_key=submission_key,
                risk_gate={"passed": False, "checks": [], "requested_price": None, "max_price": max_price, "rejection_reason": idempotency["conflict_reason"]},
                idempotency=idempotency,
                request_context={"code": code, "price": price, "quantity": quantity},
            )
        risk_gate = evaluate_trade_risk_gate(code=code, price=price, quantity=quantity, max_price=max_price)
        risk_gate = _apply_pingan_broker_readiness_required_guard(
            risk_gate,
            title_keyword=self._manager.title_keyword,
            exe_path=self._manager.exe_path,
            require_broker_readiness=require_broker_readiness,
        )
        risk_gate = _apply_pingan_lifecycle_owner_lock_required_guard(
            risk_gate,
            lifecycle_statefile_path=lifecycle_statefile_path,
            lifecycle_owner_token=lifecycle_owner_token,
            lifecycle_stale_after_seconds=lifecycle_stale_after_seconds,
            require_lifecycle_owner_lock=require_lifecycle_owner_lock,
        )
        if not risk_gate["passed"]:
            result = self._manager._build_trade_risk_rejection_result(
                code=code,
                price=price,
                quantity=quantity,
                risk_gate=risk_gate,
            )
            return self._manager._finalize_result(
                result,
                broker="pingan",
                method="buy",
                profile_options=effective_profile,
                timing={},
                submission_key=submission_key,
                risk_gate=risk_gate,
                idempotency=idempotency,
                request_context={"code": code, "price": price, "quantity": quantity},
            )
        result, timing = capture_trade_timing(
            "pingan.buy",
            lambda: run_pingan_buy_fast(
                self._manager.title_keyword,
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                hid_pre_delay=float(effective_profile["hid_pre_delay"]),
                code=code,
                price=price,
                quantity=quantity,
                post_delay=float(effective_profile["post_delay"]),
                max_depth=max_depth,
                dialog_timeout=float(effective_profile["dialog_timeout"]),
                confirm_timeout=float(effective_profile["confirm_timeout"]),
                confirm_post_delay=float(effective_profile["confirm_post_delay"]),
                result_timeout=float(effective_profile["result_timeout"]),
                price_quantity_input_mode=str(effective_profile["price_quantity_input_mode"]),
                dialog_lookup_mode=str(effective_profile["dialog_lookup_mode"]),
                close_result_dialog=close_result_dialog,
                result_close_pre_delay=float(effective_profile["result_close_pre_delay"]),
                capture_final_uia=bool(effective_profile["capture_final_uia"]),
            ),
        )
        return self._manager._finalize_result(
            result,
            broker="pingan",
            method="buy",
            profile_options=effective_profile,
            timing=timing,
            submission_key=submission_key,
            risk_gate=risk_gate,
            idempotency=idempotency,
            request_context={"code": code, "price": price, "quantity": quantity},
        )

    def buy_submit_once(
        self,
        *,
        port: str,
        code: str,
        price: str,
        quantity: int,
        baudrate: int = 115200,
        timeout: float = 2.0,
        max_depth: int = 12,
        close_result_dialog: bool = True,
        submission_key: str | None = None,
        max_price: float | None = None,
        lifecycle_statefile_path: str | None = None,
        lifecycle_owner_token: str | None = None,
        lifecycle_stale_after_seconds: float = 300.0,
        require_lifecycle_owner_lock: bool = False,
        require_broker_readiness: bool = False,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        idempotency = self._manager._evaluate_idempotency(
            broker="pingan",
            method="buy_submit_once",
            code=code,
            price=price,
            quantity=quantity,
            submission_key=submission_key,
        )
        if idempotency["decision"] == "skip_duplicate":
            result = self._manager._build_duplicate_submission_result(prior_row=idempotency["prior_row"])
            return self._manager._finalize_result(
                result,
                broker="pingan",
                method="buy_submit_once",
                profile_options=effective_profile,
                timing={},
                submission_key=submission_key,
                risk_gate={"passed": True, "checks": [], "requested_price": None, "max_price": max_price, "rejection_reason": None},
                idempotency=idempotency,
                request_context={"code": code, "price": price, "quantity": quantity},
            )
        if idempotency["decision"] == "reject_conflict":
            result = self._manager._build_submission_key_conflict_result(
                code=code,
                price=price,
                quantity=quantity,
                idempotency=idempotency,
            )
            return self._manager._finalize_result(
                result,
                broker="pingan",
                method="buy_submit_once",
                profile_options=effective_profile,
                timing={},
                submission_key=submission_key,
                risk_gate={"passed": False, "checks": [], "requested_price": None, "max_price": max_price, "rejection_reason": idempotency["conflict_reason"]},
                idempotency=idempotency,
                request_context={"code": code, "price": price, "quantity": quantity},
            )
        risk_gate = evaluate_trade_risk_gate(code=code, price=price, quantity=quantity, max_price=max_price)
        risk_gate = _apply_pingan_broker_readiness_required_guard(
            risk_gate,
            title_keyword=self._manager.title_keyword,
            exe_path=self._manager.exe_path,
            require_broker_readiness=require_broker_readiness,
        )
        risk_gate = _apply_pingan_lifecycle_owner_lock_required_guard(
            risk_gate,
            lifecycle_statefile_path=lifecycle_statefile_path,
            lifecycle_owner_token=lifecycle_owner_token,
            lifecycle_stale_after_seconds=lifecycle_stale_after_seconds,
            require_lifecycle_owner_lock=require_lifecycle_owner_lock,
        )
        if not risk_gate["passed"]:
            result = self._manager._build_trade_risk_rejection_result(
                code=code,
                price=price,
                quantity=quantity,
                risk_gate=risk_gate,
            )
            return self._manager._finalize_result(
                result,
                broker="pingan",
                method="buy_submit_once",
                profile_options=effective_profile,
                timing={},
                submission_key=submission_key,
                risk_gate=risk_gate,
                idempotency=idempotency,
                request_context={"code": code, "price": price, "quantity": quantity},
            )
        result, timing = capture_trade_timing(
            "pingan.buy_submit_once",
            lambda: run_pingan_buy_submit_once(
                self._manager.title_keyword,
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                hid_pre_delay=float(effective_profile["hid_pre_delay"]),
                code=code,
                price=price,
                quantity=quantity,
                post_delay=float(effective_profile["post_delay"]),
                max_depth=max_depth,
                dialog_timeout=float(effective_profile["dialog_timeout"]),
                confirm_timeout=float(effective_profile["confirm_timeout"]),
                confirm_post_delay=float(effective_profile["confirm_post_delay"]),
                result_timeout=float(effective_profile["result_timeout"]),
                close_result_dialog=close_result_dialog,
                result_close_pre_delay=float(effective_profile["result_close_pre_delay"]),
                capture_final_uia=bool(effective_profile["capture_final_uia"]),
            ),
        )
        return self._manager._finalize_result(
            result,
            broker="pingan",
            method="buy_submit_once",
            profile_options=effective_profile,
            timing=timing,
            submission_key=submission_key,
            risk_gate=risk_gate,
            idempotency=idempotency,
            request_context={"code": code, "price": price, "quantity": quantity},
        )

    def sell(
        self,
        *,
        port: str,
        code: str,
        price: str,
        quantity: int,
        baudrate: int = 115200,
        timeout: float = 2.0,
        max_depth: int = 12,
        close_result_dialog: bool = True,
        submission_key: str | None = None,
        max_price: float | None = None,
        lifecycle_statefile_path: str | None = None,
        lifecycle_owner_token: str | None = None,
        lifecycle_stale_after_seconds: float = 300.0,
        require_lifecycle_owner_lock: bool = False,
        require_broker_readiness: bool = False,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        idempotency = self._manager._evaluate_idempotency(
            broker="pingan",
            method="sell",
            code=code,
            price=price,
            quantity=quantity,
            submission_key=submission_key,
        )
        if idempotency["decision"] == "skip_duplicate":
            result = self._manager._build_duplicate_submission_result(prior_row=idempotency["prior_row"])
            return self._manager._finalize_result(
                result,
                broker="pingan",
                method="sell",
                profile_options=effective_profile,
                timing={},
                submission_key=submission_key,
                risk_gate={"passed": True, "checks": [], "requested_price": None, "max_price": max_price, "rejection_reason": None},
                idempotency=idempotency,
                request_context={"code": code, "price": price, "quantity": quantity},
            )
        if idempotency["decision"] == "reject_conflict":
            result = self._manager._build_submission_key_conflict_result(
                code=code,
                price=price,
                quantity=quantity,
                idempotency=idempotency,
            )
            return self._manager._finalize_result(
                result,
                broker="pingan",
                method="sell",
                profile_options=effective_profile,
                timing={},
                submission_key=submission_key,
                risk_gate={"passed": False, "checks": [], "requested_price": None, "max_price": max_price, "rejection_reason": idempotency["conflict_reason"]},
                idempotency=idempotency,
                request_context={"code": code, "price": price, "quantity": quantity},
            )
        risk_gate = evaluate_trade_risk_gate(code=code, price=price, quantity=quantity, max_price=max_price)
        risk_gate = _apply_pingan_broker_readiness_required_guard(
            risk_gate,
            title_keyword=self._manager.title_keyword,
            exe_path=self._manager.exe_path,
            require_broker_readiness=require_broker_readiness,
        )
        risk_gate = _apply_pingan_lifecycle_owner_lock_required_guard(
            risk_gate,
            lifecycle_statefile_path=lifecycle_statefile_path,
            lifecycle_owner_token=lifecycle_owner_token,
            lifecycle_stale_after_seconds=lifecycle_stale_after_seconds,
            require_lifecycle_owner_lock=require_lifecycle_owner_lock,
        )
        if not risk_gate["passed"]:
            result = self._manager._build_trade_risk_rejection_result(
                code=code,
                price=price,
                quantity=quantity,
                risk_gate=risk_gate,
            )
            return self._manager._finalize_result(
                result,
                broker="pingan",
                method="sell",
                profile_options=effective_profile,
                timing={},
                submission_key=submission_key,
                risk_gate=risk_gate,
                idempotency=idempotency,
                request_context={"code": code, "price": price, "quantity": quantity},
            )
        result, timing = capture_trade_timing(
            "pingan.sell",
            lambda: run_pingan_sell_fast(
                self._manager.title_keyword,
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                hid_pre_delay=float(effective_profile["hid_pre_delay"]),
                code=code,
                price=price,
                quantity=quantity,
                post_delay=float(effective_profile["post_delay"]),
                max_depth=max_depth,
                dialog_timeout=float(effective_profile["dialog_timeout"]),
                confirm_timeout=float(effective_profile["confirm_timeout"]),
                confirm_post_delay=float(effective_profile["confirm_post_delay"]),
                result_timeout=float(effective_profile["result_timeout"]),
                price_quantity_input_mode=str(effective_profile["price_quantity_input_mode"]),
                dialog_lookup_mode=str(effective_profile["dialog_lookup_mode"]),
                close_result_dialog=close_result_dialog,
                result_close_pre_delay=float(effective_profile["result_close_pre_delay"]),
                capture_final_uia=bool(effective_profile["capture_final_uia"]),
            ),
        )
        return self._manager._finalize_result(
            result,
            broker="pingan",
            method="sell",
            profile_options=effective_profile,
            timing=timing,
            submission_key=submission_key,
            risk_gate=risk_gate,
            idempotency=idempotency,
            request_context={"code": code, "price": price, "quantity": quantity},
        )

    def sell_submit_once(
        self,
        *,
        port: str,
        code: str,
        price: str,
        quantity: int,
        baudrate: int = 115200,
        timeout: float = 2.0,
        max_depth: int = 12,
        close_result_dialog: bool = True,
        submission_key: str | None = None,
        max_price: float | None = None,
        lifecycle_statefile_path: str | None = None,
        lifecycle_owner_token: str | None = None,
        lifecycle_stale_after_seconds: float = 300.0,
        require_lifecycle_owner_lock: bool = False,
        require_broker_readiness: bool = False,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        idempotency = self._manager._evaluate_idempotency(
            broker="pingan",
            method="sell_submit_once",
            code=code,
            price=price,
            quantity=quantity,
            submission_key=submission_key,
        )
        if idempotency["decision"] == "skip_duplicate":
            result = self._manager._build_duplicate_submission_result(prior_row=idempotency["prior_row"])
            return self._manager._finalize_result(
                result,
                broker="pingan",
                method="sell_submit_once",
                profile_options=effective_profile,
                timing={},
                submission_key=submission_key,
                risk_gate={"passed": True, "checks": [], "requested_price": None, "max_price": max_price, "rejection_reason": None},
                idempotency=idempotency,
                request_context={"code": code, "price": price, "quantity": quantity},
            )
        if idempotency["decision"] == "reject_conflict":
            result = self._manager._build_submission_key_conflict_result(
                code=code,
                price=price,
                quantity=quantity,
                idempotency=idempotency,
            )
            return self._manager._finalize_result(
                result,
                broker="pingan",
                method="sell_submit_once",
                profile_options=effective_profile,
                timing={},
                submission_key=submission_key,
                risk_gate={"passed": False, "checks": [], "requested_price": None, "max_price": max_price, "rejection_reason": idempotency["conflict_reason"]},
                idempotency=idempotency,
                request_context={"code": code, "price": price, "quantity": quantity},
            )
        risk_gate = evaluate_trade_risk_gate(code=code, price=price, quantity=quantity, max_price=max_price)
        risk_gate = _apply_pingan_broker_readiness_required_guard(
            risk_gate,
            title_keyword=self._manager.title_keyword,
            exe_path=self._manager.exe_path,
            require_broker_readiness=require_broker_readiness,
        )
        risk_gate = _apply_pingan_lifecycle_owner_lock_required_guard(
            risk_gate,
            lifecycle_statefile_path=lifecycle_statefile_path,
            lifecycle_owner_token=lifecycle_owner_token,
            lifecycle_stale_after_seconds=lifecycle_stale_after_seconds,
            require_lifecycle_owner_lock=require_lifecycle_owner_lock,
        )
        if not risk_gate["passed"]:
            result = self._manager._build_trade_risk_rejection_result(
                code=code,
                price=price,
                quantity=quantity,
                risk_gate=risk_gate,
            )
            return self._manager._finalize_result(
                result,
                broker="pingan",
                method="sell_submit_once",
                profile_options=effective_profile,
                timing={},
                submission_key=submission_key,
                risk_gate=risk_gate,
                idempotency=idempotency,
                request_context={"code": code, "price": price, "quantity": quantity},
            )
        result, timing = capture_trade_timing(
            "pingan.sell_submit_once",
            lambda: run_pingan_sell_fast(
                self._manager.title_keyword,
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                hid_pre_delay=float(effective_profile["hid_pre_delay"]),
                code=code,
                price=price,
                quantity=quantity,
                post_delay=float(effective_profile["post_delay"]),
                max_depth=max_depth,
                dialog_timeout=float(effective_profile["dialog_timeout"]),
                confirm_timeout=float(effective_profile["confirm_timeout"]),
                confirm_post_delay=float(effective_profile["confirm_post_delay"]),
                result_timeout=float(effective_profile["result_timeout"]),
                price_quantity_input_mode=str(effective_profile["price_quantity_input_mode"]),
                dialog_lookup_mode=str(effective_profile["dialog_lookup_mode"]),
                close_result_dialog=close_result_dialog,
                result_close_pre_delay=float(effective_profile["result_close_pre_delay"]),
                capture_final_uia=bool(effective_profile["capture_final_uia"]),
            ),
        )
        return self._manager._finalize_result(
            result,
            broker="pingan",
            method="sell_submit_once",
            profile_options=effective_profile,
            timing=timing,
            submission_key=submission_key,
            risk_gate=risk_gate,
            idempotency=idempotency,
            request_context={"code": code, "price": price, "quantity": quantity},
        )

    def health(
        self,
        *,
        port: str | None = None,
        baudrate: int = 115200,
        timeout: float = 2.0,
        pre_delay: float = 0.0,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})

        def run() -> Result:
            adapter = PingAnBrokerAdapter(title_keyword=self._manager.title_keyword, exe_path=self._manager.exe_path)
            broker_health = adapter.health_check()
            detect_result: Result | None = None
            checks = [
                _build_trade_health_check(
                    "broker_runtime",
                    "ok" if broker_health.ok else "failed",
                    broker_health.message,
                    detail=broker_health.to_dict(),
                    critical=True,
                    recommended_action=broker_health.next_action,
                )
            ]

            result_code = broker_health.code if not broker_health.ok else ErrorCode.OK
            if port is None:
                checks.append(
                    _build_trade_health_check(
                        "hid_ping",
                        "skipped",
                        "HID ping skipped because no serial port was requested",
                        detail={"requested_port": None},
                    )
                )
            else:
                hid_result = run_hid_ping(port=port, baudrate=baudrate, timeout=timeout, pre_delay=pre_delay)
                checks.append(
                    _build_trade_health_check(
                        "hid_ping",
                        "ok" if hid_result.ok else "failed",
                        hid_result.message,
                        detail=hid_result.to_dict(),
                        recommended_action=hid_result.next_action,
                    )
                )
                if not hid_result.ok:
                    result_code = hid_result.code

            overall_status, ok, warnings, next_action = _summarize_trade_health_checks(checks)
            if overall_status == "ok":
                message = "stable trade health check passed"
            elif ok:
                message = "stable trade health check completed with warnings"
            else:
                message = "stable trade health check found failures"

            return Result(
                ok=ok,
                code=result_code if not ok else ErrorCode.OK,
                message=message,
                data={
                    "health": {
                        "overall_status": overall_status,
                        "requested": {
                            "port": port,
                            "baudrate": baudrate,
                            "timeout": timeout,
                            "pre_delay": pre_delay,
                        },
                        "checks": checks,
                        "artifact_targets": {
                            **self._manager._artifact_targets(),
                        },
                    }
                },
                warnings=warnings,
                next_action=next_action,
            )

        result, timing = capture_trade_timing("pingan.health", run)
        attach_trade_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            broker="pingan",
            method="health",
            title_keyword=self._manager.title_keyword,
            exe_path=self._manager.exe_path,
            timing=timing,
        )
        return result

    def preflight(
        self,
        *,
        port: str,
        code: str,
        price: str,
        quantity: int,
        baudrate: int = 115200,
        timeout: float = 2.0,
        pre_delay: float = 0.0,
        submission_key: str | None = None,
        max_price: float | None = None,
        lifecycle_statefile_path: str | None = None,
        lifecycle_owner_token: str | None = None,
        lifecycle_stale_after_seconds: float = 300.0,
        require_lifecycle_owner_lock: bool = False,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})

        def run() -> Result:
            adapter = PingAnBrokerAdapter(title_keyword=self._manager.title_keyword, exe_path=self._manager.exe_path)
            broker_health = adapter.health_check()
            checks = [
                _build_trade_health_check(
                    "broker_runtime",
                    "ok" if broker_health.ok else "failed",
                    broker_health.message,
                    detail=broker_health.to_dict(),
                    critical=True,
                    recommended_action=broker_health.next_action,
                )
            ]
            result_code = broker_health.code if not broker_health.ok else ErrorCode.OK

            if broker_health.ok:
                detect_result = adapter.detect()
                checks.append(
                    _build_trade_health_check(
                        "buy_page_detection",
                        "ok" if detect_result.ok else "failed",
                        detect_result.message,
                        detail=detect_result.to_dict(),
                        critical=True,
                        recommended_action=detect_result.next_action,
                    )
                )
                if not detect_result.ok and result_code == ErrorCode.OK:
                    result_code = detect_result.code
            else:
                checks.append(
                    _build_trade_health_check(
                        "buy_page_detection",
                        "skipped",
                        "buy-page detection skipped because broker/runtime health did not pass",
                        detail={"code": code},
                        recommended_action=broker_health.next_action,
                    )
                )

            risk_gate = evaluate_trade_risk_gate(code=code, price=price, quantity=quantity, max_price=max_price)
            checks.append(
                _build_trade_health_check(
                    "risk_gate",
                    "ok" if risk_gate["passed"] else "failed",
                    "trade request passed the stable pre-trade risk gate"
                    if risk_gate["passed"]
                    else str(risk_gate.get("rejection_reason") or "stable pre-trade risk gate rejected the request"),
                    detail=risk_gate,
                    critical=True,
                    recommended_action=None if risk_gate["passed"] else "Adjust the requested trade inputs or trade safety controls, then retry.",
                )
            )
            if not risk_gate["passed"] and result_code == ErrorCode.OK:
                result_code = ErrorCode.INVALID_REQUEST

            idempotency = self._manager._evaluate_idempotency(
                broker="pingan",
                method="buy",
                code=code,
                price=price,
                quantity=quantity,
                submission_key=submission_key,
            )
            idempotency_decision = str(idempotency.get("decision"))
            if idempotency_decision == "no_submission_key":
                idempotency_status = "skipped"
                idempotency_summary = "idempotency check skipped because no submission_key was provided"
                idempotency_action = None
            elif idempotency_decision == "execute":
                idempotency_status = "ok"
                idempotency_summary = "submission_key is ready for a new stable desktop trade attempt"
                idempotency_action = None
            elif idempotency_decision == "skip_duplicate":
                idempotency_status = "warning"
                idempotency_summary = "same submission_key and normalized request already exist; execution would short-circuit"
                idempotency_action = "Use a new submission_key if you want to force a new stable desktop trade attempt."
            else:
                idempotency_status = "failed"
                idempotency_summary = str(idempotency.get("conflict_reason") or "submission_key conflicts with a prior side-effecting request")
                idempotency_action = "Use a new submission_key for a new stable desktop trade attempt."
                if result_code == ErrorCode.OK:
                    result_code = ErrorCode.INVALID_REQUEST
            checks.append(
                _build_trade_health_check(
                    "idempotency",
                    idempotency_status,
                    idempotency_summary,
                    detail=idempotency,
                    recommended_action=idempotency_action,
                )
            )

            hid_result = run_hid_ping(port=port, baudrate=baudrate, timeout=timeout, pre_delay=pre_delay)
            checks.append(
                _build_trade_health_check(
                    "hid_ping",
                    "ok" if hid_result.ok else "failed",
                    hid_result.message,
                    detail=hid_result.to_dict(),
                    critical=True,
                    recommended_action=hid_result.next_action,
                )
            )
            if not hid_result.ok and result_code == ErrorCode.OK:
                result_code = hid_result.code

            lifecycle_owner_lock_status = _build_pingan_preflight_lifecycle_owner_lock_status(
                lifecycle_statefile_path=lifecycle_statefile_path,
                lifecycle_owner_token=lifecycle_owner_token,
                lifecycle_stale_after_seconds=lifecycle_stale_after_seconds,
                require_lifecycle_owner_lock=require_lifecycle_owner_lock,
            )
            if require_lifecycle_owner_lock:
                requirement_passed = lifecycle_owner_lock_status.get("requirement_status") == "passed"
                checks.append(
                    _build_trade_health_check(
                        "lifecycle_owner_lock",
                        "ok" if requirement_passed else "failed",
                        "lifecycle owner lock requirement passed"
                        if requirement_passed
                        else str(
                            lifecycle_owner_lock_status.get("requirement_reason")
                            or "lifecycle owner lock requirement failed"
                        ),
                        detail=lifecycle_owner_lock_status,
                        critical=True,
                        recommended_action=None
                        if requirement_passed
                        else "Acquire the local PingAn lifecycle owner lock with the same owner token, then rerun preflight.",
                    )
                )
                if not requirement_passed and result_code == ErrorCode.OK:
                    result_code = ErrorCode.INVALID_REQUEST
            elif lifecycle_owner_lock_status.get("configured"):
                checks.append(
                    _build_trade_health_check(
                        "lifecycle_owner_lock",
                        "ok",
                        "lifecycle owner lock status inspected without requiring ownership",
                        detail=lifecycle_owner_lock_status,
                        critical=False,
                    )
                )

            overall_status, ok, warnings, next_action = _summarize_trade_health_checks(checks)
            if overall_status == "ok":
                message = "stable trade preflight passed"
            elif ok:
                message = "stable trade preflight completed with warnings"
            else:
                message = "stable trade preflight found failures"
            promotion_gate_status = _build_pingan_promotion_gate_status(
                broker_health=broker_health,
                detect_result=detect_result,
                risk_gate=risk_gate,
                idempotency=idempotency,
                submission_key=submission_key,
                max_price=max_price,
                lifecycle_owner_lock_status=lifecycle_owner_lock_status,
            )

            return Result(
                ok=ok,
                code=result_code if not ok else ErrorCode.OK,
                message=message,
                data={
                    "preflight": {
                        "overall_status": overall_status,
                        "requested": {
                            "port": port,
                            "baudrate": baudrate,
                            "timeout": timeout,
                            "pre_delay": pre_delay,
                            "code": code,
                            "price": price,
                            "quantity": quantity,
                            "submission_key": submission_key,
                            "max_price": max_price,
                        },
                        "checks": checks,
                        "artifact_targets": {
                            **self._manager._artifact_targets(),
                        },
                    },
                    "promotion_gate_status": promotion_gate_status,
                },
                warnings=warnings,
                next_action=next_action,
            )

        result, timing = capture_trade_timing("pingan.preflight", run)
        attach_trade_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            broker="pingan",
            method="preflight",
            title_keyword=self._manager.title_keyword,
            exe_path=self._manager.exe_path,
            timing=timing,
        )
        return result

    def dialog_readiness(
        self,
        *,
        dialog: str = "both",
        require_visible: bool = False,
        dialog_lookup_mode: str | None = None,
        confirm_timeout: float | None = None,
        result_timeout: float | None = None,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        resolved_lookup_mode = str(dialog_lookup_mode or effective_profile["dialog_lookup_mode"])
        resolved_confirm_timeout = float(
            effective_profile["confirm_timeout"] if confirm_timeout is None else confirm_timeout
        )
        resolved_result_timeout = float(
            effective_profile["result_timeout"] if result_timeout is None else result_timeout
        )

        def run() -> Result:
            checks: list[dict[str, Any]] = []

            if dialog in {"confirm", "both"}:
                confirm_target = _find_confirm_target_for_lookup(
                    title_keyword=self._manager.title_keyword,
                    lookup_mode=resolved_lookup_mode,
                    timeout=resolved_confirm_timeout,
                )
                confirm_ok = bool(confirm_target.get("ok"))
                checks.append(
                    _build_trade_health_check(
                        "confirm_lookup",
                        _resolve_dialog_check_status(found=confirm_ok, require_visible=require_visible),
                        "confirm dialog lookup matched the current dialog"
                        if confirm_ok
                        else "confirm dialog is not currently visible through the stable lookup path",
                        detail=_serialize_dialog_lookup_target(confirm_target),
                        recommended_action=(
                            None
                            if confirm_ok
                            else "Keep the confirm dialog visible and retry the readiness check."
                        ),
                    )
                )

            if dialog in {"result", "both"}:
                result_dialog = _find_result_dialog_for_lookup(
                    title_keyword=self._manager.title_keyword,
                    lookup_mode=resolved_lookup_mode,
                    timeout=resolved_result_timeout,
                )
                result_dialog_ok = bool(result_dialog.get("ok"))
                checks.append(
                    _build_trade_health_check(
                        "result_dialog_lookup",
                        _resolve_dialog_check_status(found=result_dialog_ok, require_visible=require_visible),
                        "result dialog lookup matched the current dialog"
                        if result_dialog_ok
                        else "result dialog is not currently visible through the stable lookup path",
                        detail=_serialize_dialog_lookup_target(result_dialog),
                        recommended_action=(
                            None
                            if result_dialog_ok
                            else "Keep the result dialog visible and retry the readiness check."
                        ),
                    )
                )
                if result_dialog_ok:
                    result_info = result_dialog.get("info")
                    result_hwnd = getattr(result_info, "handle", result_dialog.get("hwnd", None))
                    try:
                        exception_text_payload = _extract_dialog_text_payload_from_sources(
                            hwnd=result_hwnd,
                            element=result_dialog.get("element"),
                        )
                        exception_detail = _build_pingan_exception_popup_lookup_detail(exception_text_payload)
                    except Exception as exc:
                        exception_detail = {
                            "ok": False,
                            "exception_detected": None,
                            "matched_keywords": [],
                            "passive_texts": [],
                            "text_payload": {},
                            "last_error": str(exc),
                        }
                    exception_detected = bool(exception_detail.get("exception_detected"))
                    checks.append(
                        _build_trade_health_check(
                            "exception_popup_lookup",
                            "warning" if exception_detected else "ok",
                            "exception-like result popup text detected"
                            if exception_detected
                            else "no exception-like result popup text detected",
                            detail=exception_detail,
                            recommended_action=(
                                "Review the visible exception popup manually; dialog readiness does not close, retry, or recover it."
                                if exception_detected
                                else None
                            ),
                        )
                    )
                    result_confirm = _find_result_confirm_target_for_lookup(
                        title_keyword=self._manager.title_keyword,
                        lookup_mode=resolved_lookup_mode,
                        timeout=min(1.0, resolved_result_timeout),
                    )
                    result_confirm_ok = bool(result_confirm.get("ok"))
                    checks.append(
                        _build_trade_health_check(
                            "result_confirm_lookup",
                            _resolve_dialog_check_status(found=result_confirm_ok, require_visible=require_visible),
                            "result confirm-button lookup matched the current dialog"
                            if result_confirm_ok
                            else "result confirm button is not currently visible through the stable lookup path",
                            detail=_serialize_dialog_lookup_target(result_confirm),
                            recommended_action=(
                                None
                                if result_confirm_ok
                                else "Keep the result dialog visible and retry the readiness check."
                            ),
                        )
                    )
                else:
                    checks.append(
                        _build_trade_health_check(
                            "exception_popup_lookup",
                            "skipped",
                            "exception popup lookup skipped because the result dialog was not detected",
                            detail={
                                "ok": False,
                                "skipped": True,
                                "exception_detected": None,
                                "matched_keywords": [],
                                "text_payload": {},
                            },
                        )
                    )
                    checks.append(
                        _build_trade_health_check(
                            "result_confirm_lookup",
                            "skipped",
                            "result confirm-button lookup skipped because the result dialog was not detected",
                            detail={"ok": False, "skipped": True},
                        )
                    )

            overall_status, ok, warnings, next_action = _summarize_trade_health_checks(checks)
            if overall_status == "ok":
                message = "stable trade dialog readiness check passed"
            elif ok:
                message = "stable trade dialog readiness check completed with warnings"
            else:
                message = "stable trade dialog readiness check found failures"
            try:
                adapter = PingAnBrokerAdapter(
                    title_keyword=self._manager.title_keyword,
                    exe_path=self._manager.exe_path,
                )
                observed_process_window_ownership = _build_pingan_observed_process_window_ownership(
                    health_result=adapter.health_check(),
                    title_keyword=self._manager.title_keyword,
                    exe_path=self._manager.exe_path,
                )
            except Exception as exc:
                observed_process_window_ownership = _build_pingan_unverified_process_window_ownership(
                    title_keyword=self._manager.title_keyword,
                    exe_path=self._manager.exe_path,
                    error=exc,
                )
            retry_policy_status = _build_pingan_retry_policy_status(effective_profile)
            artifact_targets = self._manager._artifact_targets()
            statefile_lock_status = _build_pingan_statefile_lock_status(artifact_targets)
            lifecycle_control_status = _build_pingan_lifecycle_control_status(
                title_keyword=self._manager.title_keyword,
                exe_path=self._manager.exe_path,
            )
            lifecycle_gate_status = _build_pingan_desktop_lifecycle_gate_status(
                checks=checks,
                dialog=dialog,
                require_visible=require_visible,
                dialog_lookup_mode=resolved_lookup_mode,
                confirm_timeout=resolved_confirm_timeout,
                result_timeout=resolved_result_timeout,
                title_keyword=self._manager.title_keyword,
                exe_path=self._manager.exe_path,
                observed_process_window_ownership=observed_process_window_ownership,
                retry_policy_status=retry_policy_status,
                statefile_lock_status=statefile_lock_status,
                lifecycle_control_status=lifecycle_control_status,
            )
            return Result(
                ok=ok,
                code=ErrorCode.OK if ok else ErrorCode.CONTROL_NOT_FOUND,
                message=message,
                data={
                    "dialog_readiness": {
                        "overall_status": overall_status,
                        "requested": {
                            "dialog": dialog,
                            "require_visible": require_visible,
                            "dialog_lookup_mode": resolved_lookup_mode,
                            "confirm_timeout": resolved_confirm_timeout,
                            "result_timeout": resolved_result_timeout,
                        },
                        "checks": checks,
                        "artifact_targets": {
                            **artifact_targets,
                        },
                    },
                    "desktop_lifecycle_gate_status": lifecycle_gate_status,
                },
                warnings=warnings,
                next_action=next_action,
            )

        result, timing = capture_trade_timing("pingan.dialog_readiness", run)
        attach_trade_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            broker="pingan",
            method="dialog_readiness",
            title_keyword=self._manager.title_keyword,
            exe_path=self._manager.exe_path,
            timing=timing,
        )
        return result

    def exception_popup(
        self,
        *,
        action: str = "inspect",
        confirm_close: bool = False,
        dialog_lookup_mode: str | None = None,
        result_timeout: float | None = None,
        result_close_pre_delay: float | None = None,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        resolved_action = str(action or "inspect")
        resolved_lookup_mode = str(dialog_lookup_mode or effective_profile["dialog_lookup_mode"])
        resolved_result_timeout = float(
            effective_profile["result_timeout"] if result_timeout is None else result_timeout
        )
        resolved_result_close_pre_delay = float(
            effective_profile["result_close_pre_delay"]
            if result_close_pre_delay is None
            else result_close_pre_delay
        )

        def run() -> Result:
            checks: list[dict[str, Any]] = []
            if resolved_action not in {"inspect", "close"}:
                return Result(
                    ok=False,
                    code=ErrorCode.INVALID_REQUEST,
                    message="unsupported pingan exception-popup action",
                    data={
                        "input": {"action": resolved_action},
                        "exception_popup_control": {
                            "action": resolved_action,
                            "overall_status": "failed",
                            "close_executed": False,
                            "confirm_click_executed": False,
                            "order_submitted": False,
                            "retry_executed": False,
                            "recovery_executed": False,
                            "resubmission_executed": False,
                            "side_effect_level": "none",
                            "checks": [],
                        },
                    },
                )

            result_dialog = _find_result_dialog_for_lookup(
                title_keyword=self._manager.title_keyword,
                lookup_mode=resolved_lookup_mode,
                timeout=resolved_result_timeout,
            )
            result_dialog_ok = bool(result_dialog.get("ok"))
            checks.append(
                _build_trade_health_check(
                    "result_dialog_lookup",
                    "ok" if result_dialog_ok else ("failed" if resolved_action == "close" else "warning"),
                    "result dialog lookup matched the current dialog"
                    if result_dialog_ok
                    else "result dialog is not currently visible through the stable lookup path",
                    detail=_serialize_dialog_lookup_target(result_dialog),
                    recommended_action=(
                        None
                        if result_dialog_ok
                        else "Keep the exception result dialog visible and retry the exception-popup control."
                    ),
                )
            )

            exception_detail: dict[str, Any] = {
                "ok": False,
                "skipped": True,
                "exception_detected": None,
                "matched_keywords": [],
                "text_payload": {},
            }
            result_dialog_payload: dict[str, Any] = {}
            if result_dialog_ok:
                result_info = result_dialog.get("info")
                result_hwnd = getattr(result_info, "handle", result_dialog.get("hwnd", None))
                try:
                    text_payload = _extract_dialog_text_payload_from_sources(
                        hwnd=result_hwnd,
                        element=result_dialog.get("element"),
                    )
                    exception_detail = _build_pingan_exception_popup_lookup_detail(text_payload)
                except Exception as exc:
                    exception_detail = {
                        "ok": False,
                        "exception_detected": None,
                        "matched_keywords": [],
                        "passive_texts": [],
                        "text_payload": {},
                        "last_error": str(exc),
                    }
                result_dialog_payload = _serialize_dialog_lookup_target(result_dialog)
                result_dialog_payload["text_payload"] = exception_detail.get("text_payload", {})

            exception_detected = bool(exception_detail.get("exception_detected"))
            checks.append(
                _build_trade_health_check(
                    "exception_popup_lookup",
                    "warning" if exception_detected else ("ok" if result_dialog_ok else "skipped"),
                    "exception-like result popup text detected"
                    if exception_detected
                    else (
                        "no exception-like result popup text detected"
                        if result_dialog_ok
                        else "exception popup lookup skipped because the result dialog was not detected"
                    ),
                    detail=exception_detail,
                    recommended_action=(
                        "Use --action close --confirm-close only after verifying this exception popup should be closed."
                        if exception_detected
                        else None
                    ),
                )
            )

            result_confirm_target: dict[str, Any] = {"ok": False, "skipped": True}
            result_confirm_ok = False
            if result_dialog_ok:
                result_confirm_target = _find_result_confirm_target_for_lookup(
                    title_keyword=self._manager.title_keyword,
                    lookup_mode=resolved_lookup_mode,
                    timeout=min(1.0, resolved_result_timeout),
                )
                result_confirm_ok = bool(result_confirm_target.get("ok"))
                checks.append(
                    _build_trade_health_check(
                        "result_confirm_lookup",
                        "ok"
                        if result_confirm_ok
                        else ("failed" if resolved_action == "close" and exception_detected else "warning"),
                        "result confirm-button lookup matched the current dialog"
                        if result_confirm_ok
                        else "result confirm button is not currently visible through the stable lookup path",
                        detail=_serialize_dialog_lookup_target(result_confirm_target),
                        recommended_action=(
                            None
                            if result_confirm_ok
                            else "Close the visible exception popup manually before retrying desktop trading."
                        ),
                    )
                )
            else:
                checks.append(
                    _build_trade_health_check(
                        "result_confirm_lookup",
                        "skipped",
                        "result confirm-button lookup skipped because the result dialog was not detected",
                        detail={"ok": False, "skipped": True},
                    )
                )

            close_executed = False
            confirm_click_executed = False
            click_payload: dict[str, Any] = {"ok": False, "skipped": True}
            side_effect_level = "none"
            code = ErrorCode.OK
            message = "stable trade exception-popup inspect completed"
            if resolved_action == "close":
                if not confirm_close:
                    checks.append(
                        _build_trade_health_check(
                            "exception_popup_close_confirmation",
                            "failed",
                            "exception popup close requires explicit confirm_close",
                            detail={"confirm_close": confirm_close},
                            critical=True,
                            recommended_action="Re-run with --confirm-close after verifying the exception popup should be closed.",
                        )
                    )
                    code = ErrorCode.INVALID_REQUEST
                    message = "stable trade exception-popup close rejected before desktop click"
                elif not result_dialog_ok:
                    checks.append(
                        _build_trade_health_check(
                            "exception_popup_close",
                            "failed",
                            "exception popup close skipped because no result dialog was detected",
                            detail={"ok": False, "skipped": True},
                            critical=True,
                            recommended_action="Keep the exception popup visible and retry the close control.",
                        )
                    )
                    code = ErrorCode.CONTROL_NOT_FOUND
                    message = "stable trade exception-popup close could not locate the result dialog"
                elif not exception_detected:
                    checks.append(
                        _build_trade_health_check(
                            "exception_popup_close",
                            "failed",
                            "exception popup close skipped because the visible result dialog was not classified as an exception popup",
                            detail=exception_detail,
                            critical=True,
                            recommended_action="Review the dialog manually; this control only closes recognized exception-like popups.",
                        )
                    )
                    code = ErrorCode.CONTROL_NOT_FOUND
                    message = "stable trade exception-popup close skipped non-exception result dialog"
                elif not result_confirm_ok:
                    checks.append(
                        _build_trade_health_check(
                            "exception_popup_close",
                            "failed",
                            "exception popup close skipped because the result confirm control was not detected",
                            detail=_serialize_dialog_lookup_target(result_confirm_target),
                            critical=True,
                            recommended_action="Close the visible exception popup manually before retrying desktop trading.",
                        )
                    )
                    code = ErrorCode.CONTROL_NOT_FOUND
                    message = "stable trade exception-popup close could not locate the result confirm control"
                else:
                    close_result = _click_lookup_target(
                        result_confirm_target,
                        post_delay=max(0.05, resolved_result_close_pre_delay),
                    )
                    confirm_click_executed = True
                    close_executed = bool(close_result.ok)
                    click_payload = close_result.to_dict()
                    side_effect_level = "live_side_effecting"
                    checks.append(
                        _build_trade_health_check(
                            "exception_popup_close",
                            "ok" if close_result.ok else "failed",
                            close_result.message,
                            detail=click_payload,
                            critical=True,
                            recommended_action=close_result.next_action,
                        )
                    )
                    code = ErrorCode.OK if close_result.ok else close_result.code
                    message = (
                        "stable trade exception-popup close completed"
                        if close_result.ok
                        else "stable trade exception-popup close failed"
                    )
            else:
                checks.append(
                    _build_trade_health_check(
                        "exception_popup_close",
                        "skipped",
                        "exception popup close skipped because action=inspect",
                        detail={"ok": False, "skipped": True},
                    )
                )

            overall_status, summarized_ok, warnings, next_action = _summarize_trade_health_checks(checks)
            ok = summarized_ok and (code == ErrorCode.OK)
            handling_status = (
                "closed"
                if close_executed
                else ("manual_required" if exception_detected else ("not_triggered" if result_dialog_ok else "unknown"))
            )
            result = Result(
                ok=ok,
                code=code if not ok else ErrorCode.OK,
                message=message,
                data={
                    "input": {
                        "action": resolved_action,
                        "confirm_close": confirm_close,
                        "dialog_lookup_mode": resolved_lookup_mode,
                        "result_timeout": resolved_result_timeout,
                        "result_close_pre_delay": resolved_result_close_pre_delay,
                    },
                    "exception_popup_control": {
                        "overall_status": overall_status,
                        "action": resolved_action,
                        "confirm_close": confirm_close,
                        "handling_status": handling_status,
                        "handling_available": True,
                        "exception_detected": exception_detected,
                        "matched_keywords": exception_detail.get("matched_keywords", []),
                        "close_executed": close_executed,
                        "confirm_click_executed": confirm_click_executed,
                        "click_result": click_payload,
                        "order_submitted": False,
                        "retry_executed": False,
                        "recovery_executed": False,
                        "resubmission_executed": False,
                        "side_effect_level": side_effect_level,
                        "checks": checks,
                    },
                    "result_dialog": result_dialog_payload,
                },
                warnings=warnings,
                next_action=next_action,
            )
            return result

        result, timing = capture_trade_timing("pingan.exception_popup", run)
        side_effect_level = str(
            result.data.get("exception_popup_control", {}).get("side_effect_level", "none")
        )
        attach_trade_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            broker="pingan",
            method="exception_popup",
            title_keyword=self._manager.title_keyword,
            exe_path=self._manager.exe_path,
            timing=timing,
        )
        attach_trade_safety_metadata(
            result,
            submission_key=None,
            risk_gate={
                "passed": bool(result.ok),
                "checks": [
                    {
                        "name": "exception_popup_manual_close",
                        "passed": bool(result.ok),
                        "issues": [] if result.ok else [result.message],
                        "action": resolved_action,
                        "confirm_close": confirm_close,
                    }
                ],
                "requested_price": None,
                "max_price": None,
                "rejection_reason": None if result.ok else result.message,
            },
            idempotency={
                "decision": "not_applicable",
                "fingerprint": None,
                "ledger_consulted": False,
            },
            side_effect_level=side_effect_level,
        )
        return result

    def submit_ready(
        self,
        *,
        port: str,
        code: str,
        price: str,
        quantity: int,
        baudrate: int = 115200,
        timeout: float = 2.0,
        max_depth: int = 12,
        max_price: float | None = None,
        dialog_lookup_mode: str | None = None,
        confirm_timeout: float | None = None,
        lifecycle_statefile_path: str | None = None,
        lifecycle_owner_token: str | None = None,
        lifecycle_stale_after_seconds: float = 300.0,
        require_lifecycle_owner_lock: bool = False,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        resolved_lookup_mode = str(dialog_lookup_mode or effective_profile["dialog_lookup_mode"])
        resolved_confirm_timeout = float(
            effective_profile["confirm_timeout"] if confirm_timeout is None else confirm_timeout
        )
        risk_gate = evaluate_trade_risk_gate(code=code, price=price, quantity=quantity, max_price=max_price)
        risk_gate = _apply_pingan_lifecycle_owner_lock_required_guard(
            risk_gate,
            lifecycle_statefile_path=lifecycle_statefile_path,
            lifecycle_owner_token=lifecycle_owner_token,
            lifecycle_stale_after_seconds=lifecycle_stale_after_seconds,
            require_lifecycle_owner_lock=require_lifecycle_owner_lock,
        )
        if not risk_gate["passed"]:
            result = self._manager._build_trade_risk_rejection_result(
                code=code,
                price=price,
                quantity=quantity,
                risk_gate=risk_gate,
            )
            attach_trade_metadata(
                result,
                profile_name=self._manager.profile_name,
                profile_options=effective_profile,
                broker="pingan",
                method="submit_ready",
                title_keyword=self._manager.title_keyword,
                exe_path=self._manager.exe_path,
                timing={},
            )
            attach_trade_safety_metadata(
                result,
                submission_key=None,
                risk_gate=risk_gate,
                side_effect_level="none" if risk_gate.get("lifecycle_owner_lock_required_status") else "local_state_mutating",
            )
            return result

        def run() -> Result:
            probe_result = run_pingan_hid_submit_probe(
                self._manager.title_keyword,
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                code=code,
                price=price,
                quantity=quantity,
                submit_mode="quantity_tab_enter",
                post_delay=float(effective_profile["post_delay"]),
                max_depth=max_depth,
                dialog_timeout=float(effective_profile["dialog_timeout"]),
                hid_pre_delay=float(effective_profile["hid_pre_delay"]),
            )
            checks: list[dict[str, Any]] = [
                _build_trade_health_check(
                    "submit_probe",
                    "ok" if probe_result.ok else "failed",
                    probe_result.message,
                    detail=probe_result.to_dict(),
                    critical=True,
                    recommended_action=probe_result.next_action,
                )
            ]
            confirm_target: dict[str, Any] = {"ok": False, "skipped": True}
            if probe_result.ok:
                confirm_target = _find_confirm_target_for_lookup(
                    title_keyword=self._manager.title_keyword,
                    lookup_mode=resolved_lookup_mode,
                    timeout=resolved_confirm_timeout,
                )
                confirm_ok = bool(confirm_target.get("ok"))
                checks.append(
                    _build_trade_health_check(
                        "confirm_lookup",
                        "ok" if confirm_ok else "failed",
                        "confirm dialog lookup matched the current dialog"
                        if confirm_ok
                        else "confirm dialog is not currently visible through the stable lookup path",
                        detail=_serialize_dialog_lookup_target(confirm_target),
                        recommended_action=(
                            "Review the current confirm dialog manually before accepting the order."
                            if confirm_ok
                            else "Keep the confirm dialog visible and retry the submit-ready check."
                        ),
                    )
                )
            else:
                checks.append(
                    _build_trade_health_check(
                        "confirm_lookup",
                        "skipped",
                        "confirm lookup skipped because the submit probe did not reach the confirmation boundary",
                        detail={"ok": False, "skipped": True},
                    )
                )

            overall_status, ok, warnings, next_action = _summarize_trade_health_checks(checks)
            if overall_status == "ok":
                message = "stable trade submit-ready reached the confirmation boundary"
            else:
                message = "stable trade submit-ready did not reach the confirmation boundary"
            combined_warnings = list(probe_result.warnings)
            for warning in warnings:
                if warning not in combined_warnings:
                    combined_warnings.append(warning)
            return Result(
                ok=ok,
                code=ErrorCode.OK if ok else (probe_result.code if not probe_result.ok else ErrorCode.CONTROL_NOT_FOUND),
                message=message,
                data={
                    "submit_ready": {
                        "overall_status": overall_status,
                        "manual_confirmation_required": bool(probe_result.ok),
                        "requested": {
                            "port": port,
                            "baudrate": baudrate,
                            "timeout": timeout,
                            "code": code,
                            "price": price,
                            "quantity": quantity,
                            "max_depth": max_depth,
                            "max_price": max_price,
                            "dialog_lookup_mode": resolved_lookup_mode,
                            "confirm_timeout": resolved_confirm_timeout,
                            "lifecycle_statefile_path": lifecycle_statefile_path,
                            "lifecycle_owner_token": lifecycle_owner_token,
                            "lifecycle_stale_after_seconds": lifecycle_stale_after_seconds,
                            "require_lifecycle_owner_lock": require_lifecycle_owner_lock,
                        },
                        "checks": checks,
                        "submit_probe": probe_result.to_dict(),
                    }
                },
                warnings=combined_warnings,
                next_action=next_action,
            )

        result, timing = capture_trade_timing("pingan.submit_ready", run)
        attach_trade_metadata(
            result,
            profile_name=self._manager.profile_name,
            profile_options=effective_profile,
            broker="pingan",
            method="submit_ready",
            title_keyword=self._manager.title_keyword,
            exe_path=self._manager.exe_path,
            timing=timing,
        )
        attach_trade_safety_metadata(
            result,
            submission_key=None,
            risk_gate=risk_gate,
            side_effect_level="local_state_mutating",
        )
        return result

    def confirm_current(
        self,
        *,
        dialog_lookup_mode: str | None = None,
        confirm_timeout: float | None = None,
        result_timeout: float | None = None,
        close_result_dialog: bool = True,
        result_close_pre_delay: float | None = None,
        lifecycle_statefile_path: str | None = None,
        lifecycle_owner_token: str | None = None,
        lifecycle_stale_after_seconds: float = 300.0,
        require_lifecycle_owner_lock: bool = False,
        require_broker_readiness: bool = False,
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        resolved_lookup_mode = str(dialog_lookup_mode or effective_profile["dialog_lookup_mode"])
        resolved_confirm_timeout = float(
            effective_profile["confirm_timeout"] if confirm_timeout is None else confirm_timeout
        )
        resolved_result_timeout = float(
            effective_profile["result_timeout"] if result_timeout is None else result_timeout
        )
        resolved_result_close_pre_delay = float(
            effective_profile["result_close_pre_delay"]
            if result_close_pre_delay is None
            else result_close_pre_delay
        )
        boundary_risk_gate = {
            "passed": True,
            "checks": [
                {
                    "name": "confirm_boundary",
                    "passed": True,
                    "issues": [],
                    "mode": "current_confirm_dialog",
                }
            ],
            "requested_price": None,
            "max_price": None,
            "rejection_reason": None,
        }
        boundary_risk_gate = _apply_pingan_broker_readiness_required_guard(
            boundary_risk_gate,
            title_keyword=self._manager.title_keyword,
            exe_path=self._manager.exe_path,
            require_broker_readiness=require_broker_readiness,
        )
        boundary_risk_gate = _apply_pingan_lifecycle_owner_lock_required_guard(
            boundary_risk_gate,
            lifecycle_statefile_path=lifecycle_statefile_path,
            lifecycle_owner_token=lifecycle_owner_token,
            lifecycle_stale_after_seconds=lifecycle_stale_after_seconds,
            require_lifecycle_owner_lock=require_lifecycle_owner_lock,
        )
        if not boundary_risk_gate["passed"]:
            broker_readiness_status = boundary_risk_gate.get("broker_readiness_required_status", {})
            owner_lock_status = boundary_risk_gate.get("lifecycle_owner_lock_required_status", {})
            failed_broker_readiness = (
                isinstance(broker_readiness_status, dict)
                and broker_readiness_status.get("requirement_status") == "failed"
            )
            failed_status = broker_readiness_status if failed_broker_readiness else owner_lock_status
            failed_check_name = "broker_readiness_required" if failed_broker_readiness else "lifecycle_owner_lock_required"
            failed_message = (
                "stable trade confirm-current rejected by broker readiness requirement"
                if failed_broker_readiness
                else "stable trade confirm-current rejected by lifecycle owner-lock requirement"
            )
            failed_next_action = (
                broker_readiness_status.get("broker_health", {}).get("next_action")
                if failed_broker_readiness and isinstance(broker_readiness_status.get("broker_health"), dict)
                else None
            ) or (
                "Bring Ping An to the foreground and retry confirm-current."
                if failed_broker_readiness
                else "Acquire the PingAn lifecycle owner lock and retry confirm-current."
            )
            failed_code = (
                ErrorCode(str(broker_readiness_status.get("broker_health", {}).get("code")))
                if failed_broker_readiness
                and isinstance(broker_readiness_status.get("broker_health"), dict)
                and broker_readiness_status.get("broker_health", {}).get("code") in ErrorCode._value2member_map_
                else ErrorCode.INVALID_REQUEST
            )
            result = Result(
                ok=False,
                code=failed_code,
                message=failed_message,
                data={
                    "input": {
                        "boundary": "confirm_current",
                        "close_result_dialog": close_result_dialog,
                        "dialog_lookup_mode": resolved_lookup_mode,
                        "confirm_timeout": resolved_confirm_timeout,
                        "result_timeout": resolved_result_timeout,
                        "lifecycle_statefile_path": lifecycle_statefile_path,
                        "lifecycle_owner_token": lifecycle_owner_token,
                        "lifecycle_stale_after_seconds": lifecycle_stale_after_seconds,
                        "require_lifecycle_owner_lock": require_lifecycle_owner_lock,
                        "require_broker_readiness": require_broker_readiness,
                    },
                    "confirm_current": {
                        "overall_status": "failed",
                        "confirmation_advanced": False,
                        "result_dialog_closed": False,
                        "requested": {
                            "close_result_dialog": close_result_dialog,
                            "dialog_lookup_mode": resolved_lookup_mode,
                            "confirm_timeout": resolved_confirm_timeout,
                            "result_timeout": resolved_result_timeout,
                            "result_close_pre_delay": resolved_result_close_pre_delay,
                        },
                        "checks": [
                            _build_trade_health_check(
                                failed_check_name,
                                "failed",
                                str(
                                    failed_status.get("requirement_reason")
                                    or (
                                        "broker readiness requirement failed"
                                        if failed_broker_readiness
                                        else "lifecycle owner lock requirement failed"
                                    )
                                ),
                                detail=failed_status,
                                critical=True,
                                recommended_action=failed_next_action,
                            )
                        ],
                    },
                    "result_dialog": {},
                },
                next_action=failed_next_action,
            )
            attach_trade_metadata(
                result,
                profile_name=self._manager.profile_name,
                profile_options=effective_profile,
                broker="pingan",
                method="confirm_current",
                title_keyword=self._manager.title_keyword,
                exe_path=self._manager.exe_path,
                timing={},
            )
            attach_trade_safety_metadata(
                result,
                submission_key=None,
                risk_gate=boundary_risk_gate,
                idempotency={"decision": "not_applicable", "fingerprint": None, "ledger_consulted": False},
                side_effect_level="none",
            )
            return result

        def run() -> Result:
            checks: list[dict[str, Any]] = []
            confirm_target = _find_confirm_target_for_lookup(
                title_keyword=self._manager.title_keyword,
                lookup_mode=resolved_lookup_mode,
                timeout=resolved_confirm_timeout,
            )
            confirm_ok = bool(confirm_target.get("ok"))
            checks.append(
                _build_trade_health_check(
                    "confirm_lookup",
                    "ok" if confirm_ok else "failed",
                    "confirm dialog lookup matched the current dialog"
                    if confirm_ok
                    else "confirm dialog is not currently visible through the stable lookup path",
                    detail=_serialize_dialog_lookup_target(confirm_target),
                    recommended_action=(
                        "Advance the current confirm dialog only after verifying it belongs to the intended order."
                        if confirm_ok
                        else "Keep the current confirm dialog visible and retry the confirm-current workflow."
                    ),
                )
            )
            if not confirm_ok:
                overall_status, ok, warnings, next_action = _summarize_trade_health_checks(checks)
                return Result(
                    ok=ok,
                    code=ErrorCode.CONTROL_NOT_FOUND,
                    message="stable trade confirm-current could not locate the current confirm dialog",
                    data={
                        "input": {
                            "boundary": "confirm_current",
                            "close_result_dialog": close_result_dialog,
                            "dialog_lookup_mode": resolved_lookup_mode,
                            "confirm_timeout": resolved_confirm_timeout,
                            "result_timeout": resolved_result_timeout,
                        },
                        "confirm_current": {
                            "overall_status": overall_status,
                            "confirmation_advanced": False,
                            "result_dialog_closed": False,
                            "requested": {
                                "close_result_dialog": close_result_dialog,
                                "dialog_lookup_mode": resolved_lookup_mode,
                                "confirm_timeout": resolved_confirm_timeout,
                                "result_timeout": resolved_result_timeout,
                                "result_close_pre_delay": resolved_result_close_pre_delay,
                            },
                            "checks": checks,
                        },
                        "result_dialog": {},
                    },
                    warnings=warnings,
                    next_action=next_action,
                )

            confirm_click = _click_lookup_target(confirm_target, post_delay=float(effective_profile["confirm_post_delay"]))
            checks.append(
                _build_trade_health_check(
                    "confirm_click",
                    "ok" if confirm_click.ok else "failed",
                    confirm_click.message,
                    detail=confirm_click.to_dict(),
                    critical=True,
                    recommended_action=confirm_click.next_action,
                )
            )
            if not confirm_click.ok:
                overall_status, ok, warnings, next_action = _summarize_trade_health_checks(checks)
                return Result(
                    ok=ok,
                    code=confirm_click.code,
                    message="stable trade confirm-current failed while advancing the current confirm dialog",
                    data={
                        "input": {
                            "boundary": "confirm_current",
                            "close_result_dialog": close_result_dialog,
                            "dialog_lookup_mode": resolved_lookup_mode,
                            "confirm_timeout": resolved_confirm_timeout,
                            "result_timeout": resolved_result_timeout,
                        },
                        "confirm_current": {
                            "overall_status": overall_status,
                            "confirmation_advanced": False,
                            "result_dialog_closed": False,
                            "requested": {
                                "close_result_dialog": close_result_dialog,
                                "dialog_lookup_mode": resolved_lookup_mode,
                                "confirm_timeout": resolved_confirm_timeout,
                                "result_timeout": resolved_result_timeout,
                                "result_close_pre_delay": resolved_result_close_pre_delay,
                            },
                            "checks": checks,
                        },
                        "result_dialog": {},
                    },
                    warnings=warnings,
                    next_action=next_action,
                )

            result_dialog = _find_result_dialog_for_lookup(
                title_keyword=self._manager.title_keyword,
                lookup_mode=resolved_lookup_mode,
                timeout=resolved_result_timeout,
            )
            result_dialog_ok = bool(result_dialog.get("ok"))
            checks.append(
                _build_trade_health_check(
                    "result_dialog_lookup",
                    "ok" if result_dialog_ok else "warning",
                    "result dialog lookup matched the current dialog"
                    if result_dialog_ok
                    else "result dialog was not detected after the current confirm click",
                    detail=_serialize_dialog_lookup_target(result_dialog),
                    recommended_action=(
                        None
                        if result_dialog_ok
                        else "Verify the order outcome manually and close any visible result dialog if needed."
                    ),
                )
            )

            result_dialog_payload: dict[str, Any] = {}
            result_dialog_closed = False
            if result_dialog_ok:
                result_info = result_dialog["info"]
                result_dialog_payload = _safe_serialize_runtime_element(result_dialog["element"], result_info) | _extract_dialog_text_payload_from_sources(
                    hwnd=getattr(result_info, "handle", None),
                    element=result_dialog.get("element"),
                )
                result_dialog_payload["lookup_mode"] = result_dialog.get("lookup_mode", resolved_lookup_mode)
                if result_dialog.get("lookup_fallback_from"):
                    result_dialog_payload["lookup_fallback_from"] = result_dialog.get("lookup_fallback_from")

            if close_result_dialog and result_dialog_ok:
                result_confirm_target = _find_result_confirm_target_for_lookup(
                    title_keyword=self._manager.title_keyword,
                    lookup_mode=resolved_lookup_mode,
                    timeout=min(1.0, resolved_result_timeout),
                )
                result_confirm_ok = bool(result_confirm_target.get("ok"))
                checks.append(
                    _build_trade_health_check(
                        "result_confirm_lookup",
                        "ok" if result_confirm_ok else "warning",
                        "result confirm-button lookup matched the current dialog"
                        if result_confirm_ok
                        else "result confirm button is not currently visible through the stable lookup path",
                        detail=_serialize_dialog_lookup_target(result_confirm_target),
                        recommended_action=(
                            None
                            if result_confirm_ok
                            else "Close the visible result dialog manually before the next order."
                        ),
                    )
                )
                if result_confirm_ok:
                    result_close = _click_lookup_target(
                        result_confirm_target,
                        post_delay=max(0.05, resolved_result_close_pre_delay),
                    )
                    result_dialog_closed = bool(result_close.ok)
                    checks.append(
                        _build_trade_health_check(
                            "result_dialog_close",
                            "ok" if result_close.ok else "warning",
                            result_close.message,
                            detail=result_close.to_dict(),
                            recommended_action=(
                                None
                                if result_close.ok
                                else "Close the result dialog manually before the next order."
                            ),
                        )
                    )
                else:
                    checks.append(
                        _build_trade_health_check(
                            "result_dialog_close",
                            "skipped",
                            "result dialog close skipped because the result confirm control was not detected",
                            detail={"ok": False, "skipped": True},
                        )
                    )
            else:
                checks.append(
                    _build_trade_health_check(
                        "result_dialog_close",
                        "skipped",
                        "result dialog close skipped because auto close is disabled or no result dialog was detected",
                        detail={"ok": False, "skipped": True},
                    )
                )

            overall_status, ok, warnings, next_action = _summarize_trade_health_checks(checks)
            if overall_status == "ok":
                message = "stable trade confirm-current advanced the current confirmation"
            else:
                message = "stable trade confirm-current completed with warnings"
            return Result(
                ok=ok,
                code=ErrorCode.OK if ok else ErrorCode.EXECUTION_FAILED,
                message=message,
                data={
                    "input": {
                        "boundary": "confirm_current",
                        "close_result_dialog": close_result_dialog,
                        "dialog_lookup_mode": resolved_lookup_mode,
                        "confirm_timeout": resolved_confirm_timeout,
                        "result_timeout": resolved_result_timeout,
                    },
                    "confirm_current": {
                        "overall_status": overall_status,
                        "confirmation_advanced": True,
                        "result_dialog_closed": result_dialog_closed,
                        "requested": {
                            "close_result_dialog": close_result_dialog,
                            "dialog_lookup_mode": resolved_lookup_mode,
                            "confirm_timeout": resolved_confirm_timeout,
                            "result_timeout": resolved_result_timeout,
                            "result_close_pre_delay": resolved_result_close_pre_delay,
                        },
                        "checks": checks,
                    },
                    "result_dialog": result_dialog_payload,
                },
                warnings=warnings,
                next_action=next_action,
            )

        result, timing = capture_trade_timing("pingan.confirm_current", run)
        confirmation_advanced = bool(result.data.get("confirm_current", {}).get("confirmation_advanced"))
        if not confirmation_advanced:
            attach_trade_metadata(
                result,
                profile_name=self._manager.profile_name,
                profile_options=effective_profile,
                broker="pingan",
                method="confirm_current",
                title_keyword=self._manager.title_keyword,
                exe_path=self._manager.exe_path,
                timing=timing,
            )
            attach_trade_safety_metadata(
                result,
                submission_key=None,
                risk_gate=boundary_risk_gate,
                idempotency={"decision": "not_applicable", "fingerprint": None, "ledger_consulted": False},
            )
            return result
        return self._manager._finalize_result(
            result,
            broker="pingan",
            method="confirm_current",
            profile_options=effective_profile,
            timing=timing,
            submission_key=None,
            risk_gate=boundary_risk_gate,
            idempotency={"decision": "not_applicable", "fingerprint": None, "ledger_consulted": False},
            request_context=None,
        )


class TdxTradeManager:
    __slots__ = (
        "profile_name",
        "profile_options",
        "title_keyword",
        "exe_path",
        "state_path",
        "event_log_path",
        "submission_ledger_path",
        "trade_audit_dir",
        "pingan",
    )

    def __init__(
        self,
        *,
        profile: str = "balanced",
        title_keyword: str = "平安证券",
        exe_path: str | None = None,
        profile_overrides: dict[str, Any] | None = None,
        state_path: str | None = None,
        event_log_path: str | None = None,
        submission_ledger_path: str | None = None,
        trade_audit_dir: str | None = None,
    ) -> None:
        self.profile_name = profile
        self.profile_options = resolve_trade_profile(profile, overrides=profile_overrides)
        self.title_keyword = title_keyword
        self.exe_path = exe_path
        self.state_path = state_path
        self.event_log_path = event_log_path
        self.submission_ledger_path = submission_ledger_path
        self.trade_audit_dir = trade_audit_dir
        self.pingan = _PingAnTradeProxy(self)

    def _build_effective_profile(self, overrides: dict[str, Any]) -> dict[str, Any]:
        effective = dict(self.profile_options)
        for key, value in overrides.items():
            effective[key] = value
        return effective

    def _artifact_targets(self) -> dict[str, str]:
        return {
            "last_order_state_path": str(
                Path(self.state_path) if self.state_path is not None else get_pingan_last_order_state_path()
            ),
            "order_event_log_path": str(
                Path(self.event_log_path) if self.event_log_path is not None else get_pingan_order_event_log_path()
            ),
            "submission_ledger_path": str(
                Path(self.submission_ledger_path)
                if self.submission_ledger_path is not None
                else get_pingan_submission_ledger_path()
            ),
            "trade_audit_dir": str(
                Path(self.trade_audit_dir)
                if self.trade_audit_dir is not None
                else get_pingan_trade_audit_dir()
            ),
        }

    def _finalize_result(
        self,
        result: Result,
        *,
        broker: str,
        method: str,
        profile_options: dict[str, Any],
        timing: dict[str, Any],
        submission_key: str | None = None,
        risk_gate: dict[str, Any] | None = None,
        idempotency: dict[str, Any] | None = None,
        request_context: dict[str, Any] | None = None,
    ) -> Result:
        attach_trade_metadata(
            result,
            profile_name=self.profile_name,
            profile_options=profile_options,
            broker=broker,
            method=method,
            title_keyword=self.title_keyword,
            exe_path=self.exe_path,
            timing=timing,
        )
        attach_trade_safety_metadata(
            result,
            submission_key=submission_key,
            risk_gate=risk_gate or {"passed": True, "checks": [], "requested_price": None, "max_price": None, "rejection_reason": None},
            idempotency=idempotency,
        )
        attach_trade_audit_metadata(
            result,
            broker=broker,
            method=method,
            submission_key=submission_key,
            risk_gate=risk_gate or {"passed": True, "checks": [], "requested_price": None, "max_price": None, "rejection_reason": None},
            idempotency=idempotency,
        )
        state_path = write_pingan_last_order_state(result, state_path=None if self.state_path is None else Path(self.state_path))
        event_log_path = append_pingan_order_event(result, log_path=None if self.event_log_path is None else Path(self.event_log_path))
        result.data.setdefault("artifacts", {})["last_order_state_path"] = str(state_path)
        result.data.setdefault("artifacts", {})["order_event_log_path"] = str(event_log_path)
        if submission_key is not None and request_context is not None:
            ledger_path = append_pingan_submission_ledger_entry(
                result,
                submission_key=submission_key,
                broker=broker,
                method=method,
                code=str(request_context["code"]),
                price=str(request_context["price"]),
                quantity=int(request_context["quantity"]),
                ledger_path=None if self.submission_ledger_path is None else Path(self.submission_ledger_path),
            )
            result.data.setdefault("artifacts", {})["submission_ledger_path"] = str(ledger_path)
        trade_audit_path = write_pingan_trade_audit(
            result,
            audit_dir=None if self.trade_audit_dir is None else Path(self.trade_audit_dir),
        )
        result.data.setdefault("artifacts", {})["trade_audit_path"] = str(trade_audit_path)
        result.data["trade_audit_gate_status"] = _build_pingan_trade_audit_gate_status(result)
        return result

    def _build_trade_risk_rejection_result(
        self,
        *,
        code: str,
        price: str,
        quantity: int,
        risk_gate: dict[str, Any],
    ) -> Result:
        rejection_reason = str(risk_gate.get("rejection_reason") or "pre-trade risk gate rejected desktop trade request")
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message=rejection_reason,
            data={
                "input": {
                    "code": code,
                    "price": price,
                    "quantity": quantity,
                }
            },
            next_action="Adjust the order request or trade safety controls, then retry.",
        )

    def _build_submission_key_conflict_result(
        self,
        *,
        code: str,
        price: str,
        quantity: int,
        idempotency: dict[str, Any],
    ) -> Result:
        return Result(
            ok=False,
            code=ErrorCode.INVALID_REQUEST,
            message=str(idempotency.get("conflict_reason") or "submission_key conflict"),
            data={
                "input": {
                    "code": code,
                    "price": price,
                    "quantity": quantity,
                }
            },
            next_action="Use a new submission_key for a new desktop trade attempt.",
        )

    def _build_duplicate_submission_result(self, *, prior_row: dict[str, Any] | None) -> Result:
        result = build_result_from_submission_ledger_row(prior_row or {})
        result.warnings.append("duplicate submission_key skipped; returning prior outcome")
        return result

    def _evaluate_idempotency(
        self,
        *,
        broker: str,
        method: str,
        code: str,
        price: str,
        quantity: int,
        submission_key: str | None,
    ) -> dict[str, Any]:
        return evaluate_trade_submission_idempotency(
            submission_key=submission_key,
            broker=broker,
            method=method,
            code=code,
            price=price,
            quantity=quantity,
            ledger_path=None if self.submission_ledger_path is None else Path(self.submission_ledger_path),
        )
