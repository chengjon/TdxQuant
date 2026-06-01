from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ..models import ErrorCode, Result
from .context import capture_trade_timing


@dataclass(frozen=True)
class PingAnExecutionRequest:
    method: str
    timing_label: str
    code: str
    price: str
    quantity: int
    submission_key: str | None
    max_price: float | None
    profile_options: dict[str, Any]
    broker: str = "pingan"

    def request_context(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "price": self.price,
            "quantity": self.quantity,
        }


@dataclass(frozen=True)
class PingAnOrderExecutionHandlers:
    build_duplicate_submission_result: Callable[[Any], Result]
    build_submission_key_conflict_result: Callable[[dict[str, Any]], Result]
    build_trade_risk_rejection_result: Callable[[dict[str, Any]], Result]
    finalize_result: Callable[..., Result]


@dataclass(frozen=True)
class PingAnConfirmCurrentExecutionRequest:
    method: str
    timing_label: str
    profile_options: dict[str, Any]
    broker: str = "pingan"

    def request_context(self) -> None:
        return None


@dataclass(frozen=True)
class PingAnConfirmCurrentRejectionContext:
    close_result_dialog: bool
    dialog_lookup_mode: str
    confirm_timeout: float
    result_timeout: float
    result_close_pre_delay: float
    lifecycle_statefile_path: str | None
    lifecycle_owner_token: str | None
    lifecycle_stale_after_seconds: float
    require_lifecycle_owner_lock: bool
    require_broker_readiness: bool


@dataclass(frozen=True)
class PingAnConfirmCurrentDispatchContext:
    close_result_dialog: bool
    dialog_lookup_mode: str
    confirm_timeout: float
    result_timeout: float
    result_close_pre_delay: float


def _confirm_health_check(
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


def _not_applicable_idempotency() -> dict[str, Any]:
    return {"decision": "not_applicable", "fingerprint": None, "ledger_consulted": False}


def build_pingan_confirm_current_boundary_rejection_result(
    risk_gate: dict[str, Any],
    *,
    context: PingAnConfirmCurrentRejectionContext,
) -> Result:
    broker_readiness_status = risk_gate.get("broker_readiness_required_status", {})
    owner_lock_status = risk_gate.get("lifecycle_owner_lock_required_status", {})
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
    return Result(
        ok=False,
        code=failed_code,
        message=failed_message,
        data={
            "input": {
                "boundary": "confirm_current",
                "close_result_dialog": context.close_result_dialog,
                "dialog_lookup_mode": context.dialog_lookup_mode,
                "confirm_timeout": context.confirm_timeout,
                "result_timeout": context.result_timeout,
                "lifecycle_statefile_path": context.lifecycle_statefile_path,
                "lifecycle_owner_token": context.lifecycle_owner_token,
                "lifecycle_stale_after_seconds": context.lifecycle_stale_after_seconds,
                "require_lifecycle_owner_lock": context.require_lifecycle_owner_lock,
                "require_broker_readiness": context.require_broker_readiness,
            },
            "confirm_current": {
                "overall_status": "failed",
                "confirmation_advanced": False,
                "result_dialog_closed": False,
                "requested": {
                    "close_result_dialog": context.close_result_dialog,
                    "dialog_lookup_mode": context.dialog_lookup_mode,
                    "confirm_timeout": context.confirm_timeout,
                    "result_timeout": context.result_timeout,
                    "result_close_pre_delay": context.result_close_pre_delay,
                },
                "checks": [
                    _confirm_health_check(
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


def build_pingan_confirm_current_dispatch_result(
    *,
    context: PingAnConfirmCurrentDispatchContext,
    ok: bool,
    code: ErrorCode,
    message: str,
    checks: list[dict[str, Any]],
    overall_status: str,
    confirmation_advanced: bool,
    result_dialog_closed: bool,
    result_dialog_payload: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    next_action: str | None = None,
) -> Result:
    return Result(
        ok=ok,
        code=code,
        message=message,
        data={
            "input": {
                "boundary": "confirm_current",
                "close_result_dialog": context.close_result_dialog,
                "dialog_lookup_mode": context.dialog_lookup_mode,
                "confirm_timeout": context.confirm_timeout,
                "result_timeout": context.result_timeout,
            },
            "confirm_current": {
                "overall_status": overall_status,
                "confirmation_advanced": confirmation_advanced,
                "result_dialog_closed": result_dialog_closed,
                "requested": {
                    "close_result_dialog": context.close_result_dialog,
                    "dialog_lookup_mode": context.dialog_lookup_mode,
                    "confirm_timeout": context.confirm_timeout,
                    "result_timeout": context.result_timeout,
                    "result_close_pre_delay": context.result_close_pre_delay,
                },
                "checks": checks,
            },
            "result_dialog": dict(result_dialog_payload or {}),
        },
        warnings=list(warnings or []),
        next_action=next_action,
    )


def _duplicate_risk_gate(request: PingAnExecutionRequest) -> dict[str, Any]:
    return {
        "passed": True,
        "checks": [],
        "requested_price": None,
        "max_price": request.max_price,
        "rejection_reason": None,
    }


def _conflict_risk_gate(
    request: PingAnExecutionRequest,
    idempotency: dict[str, Any],
) -> dict[str, Any]:
    return {
        "passed": False,
        "checks": [],
        "requested_price": None,
        "max_price": request.max_price,
        "rejection_reason": idempotency.get("conflict_reason"),
    }


def execute_pingan_order(
    request: PingAnExecutionRequest,
    *,
    idempotency: dict[str, Any],
    risk_gate: dict[str, Any],
    dispatch: Callable[[], Result],
    handlers: PingAnOrderExecutionHandlers | None = None,
    build_duplicate_submission_result: Callable[[Any], Result] | None = None,
    build_submission_key_conflict_result: Callable[[dict[str, Any]], Result] | None = None,
    build_trade_risk_rejection_result: Callable[[dict[str, Any]], Result] | None = None,
    finalize_result: Callable[..., Result] | None = None,
    capture_timing: Callable[[str, Callable[[], Result]], tuple[Result, dict[str, Any]]] = capture_trade_timing,
) -> Result:
    if handlers is None:
        if (
            build_duplicate_submission_result is None
            or build_submission_key_conflict_result is None
            or build_trade_risk_rejection_result is None
            or finalize_result is None
        ):
            raise TypeError("execute_pingan_order requires handlers or all legacy result callbacks")
        handlers = PingAnOrderExecutionHandlers(
            build_duplicate_submission_result=build_duplicate_submission_result,
            build_submission_key_conflict_result=build_submission_key_conflict_result,
            build_trade_risk_rejection_result=build_trade_risk_rejection_result,
            finalize_result=finalize_result,
        )
    decision = str(idempotency.get("decision") or "execute")
    timing: dict[str, Any] = {}
    final_risk_gate = risk_gate

    if decision == "skip_duplicate":
        result = handlers.build_duplicate_submission_result(idempotency.get("prior_row"))
        final_risk_gate = _duplicate_risk_gate(request)
    elif decision == "reject_conflict":
        result = handlers.build_submission_key_conflict_result(idempotency)
        final_risk_gate = _conflict_risk_gate(request, idempotency)
    elif not bool(risk_gate.get("passed")):
        result = handlers.build_trade_risk_rejection_result(risk_gate)
    else:
        result, timing = capture_timing(request.timing_label, dispatch)

    return handlers.finalize_result(
        result,
        broker=request.broker,
        method=request.method,
        profile_options=request.profile_options,
        timing=timing,
        submission_key=request.submission_key,
        risk_gate=final_risk_gate,
        idempotency=idempotency,
        request_context=request.request_context(),
    )


def execute_pingan_confirm_current(
    request: PingAnConfirmCurrentExecutionRequest,
    *,
    risk_gate: dict[str, Any],
    dispatch: Callable[[], Result],
    build_rejected_result: Callable[[dict[str, Any]], Result],
    attach_metadata: Callable[[Result, dict[str, Any]], Result],
    attach_safety_metadata: Callable[[Result, dict[str, Any], dict[str, Any], str | None], Result],
    finalize_result: Callable[..., Result],
    capture_timing: Callable[[str, Callable[[], Result]], tuple[Result, dict[str, Any]]] = capture_trade_timing,
) -> Result:
    idempotency = _not_applicable_idempotency()

    if not bool(risk_gate.get("passed")):
        result = build_rejected_result(risk_gate)
        attach_metadata(result, {})
        attach_safety_metadata(result, risk_gate, idempotency, "none")
        return result

    result, timing = capture_timing(request.timing_label, dispatch)
    confirm_current = result.data.get("confirm_current", {}) if isinstance(result.data, dict) else {}
    confirmation_advanced = bool(confirm_current.get("confirmation_advanced"))
    if not confirmation_advanced:
        attach_metadata(result, timing)
        attach_safety_metadata(result, risk_gate, idempotency, None)
        return result

    return finalize_result(
        result,
        broker=request.broker,
        method=request.method,
        profile_options=request.profile_options,
        timing=timing,
        submission_key=None,
        risk_gate=risk_gate,
        idempotency=idempotency,
        request_context=request.request_context(),
    )
