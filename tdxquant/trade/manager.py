from __future__ import annotations

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


def _build_pingan_promotion_gate_status(
    *,
    broker_health: Result,
    detect_result: Result | None,
    risk_gate: dict[str, Any],
    idempotency: dict[str, Any],
    submission_key: str | None,
    max_price: float | None,
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
) -> dict[str, Any]:
    dialog_checks = _extract_dialog_lifecycle_checks(checks)
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
        "covered_lifecycle_gates": [
            name
            for name in ("confirm_lookup", "result_dialog_lookup", "result_confirm_lookup")
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
        if name not in {"confirm_lookup", "result_dialog_lookup", "result_confirm_lookup"}:
            continue
        dialog_checks[str(name)] = {
            "status": check.get("status"),
            "summary": check.get("summary"),
            "detail": check.get("detail"),
        }
    return dialog_checks


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
            lifecycle_gate_status = _build_pingan_desktop_lifecycle_gate_status(
                checks=checks,
                dialog=dialog,
                require_visible=require_visible,
                dialog_lookup_mode=resolved_lookup_mode,
                confirm_timeout=resolved_confirm_timeout,
                result_timeout=resolved_result_timeout,
                title_keyword=self._manager.title_keyword,
                exe_path=self._manager.exe_path,
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
                            **self._manager._artifact_targets(),
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
    ) -> Result:
        effective_profile = self._manager._build_effective_profile({})
        resolved_lookup_mode = str(dialog_lookup_mode or effective_profile["dialog_lookup_mode"])
        resolved_confirm_timeout = float(
            effective_profile["confirm_timeout"] if confirm_timeout is None else confirm_timeout
        )
        risk_gate = evaluate_trade_risk_gate(code=code, price=price, quantity=quantity, max_price=max_price)
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
                side_effect_level="local_state_mutating",
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
