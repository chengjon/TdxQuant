from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ..models import Result
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
    build_duplicate_submission_result: Callable[[Any], Result],
    build_submission_key_conflict_result: Callable[[dict[str, Any]], Result],
    build_trade_risk_rejection_result: Callable[[dict[str, Any]], Result],
    finalize_result: Callable[..., Result],
    capture_timing: Callable[[str, Callable[[], Result]], tuple[Result, dict[str, Any]]] = capture_trade_timing,
) -> Result:
    decision = str(idempotency.get("decision") or "execute")
    timing: dict[str, Any] = {}
    final_risk_gate = risk_gate

    if decision == "skip_duplicate":
        result = build_duplicate_submission_result(idempotency.get("prior_row"))
        final_risk_gate = _duplicate_risk_gate(request)
    elif decision == "reject_conflict":
        result = build_submission_key_conflict_result(idempotency)
        final_risk_gate = _conflict_risk_gate(request, idempotency)
    elif not bool(risk_gate.get("passed")):
        result = build_trade_risk_rejection_result(risk_gate)
    else:
        result, timing = capture_timing(request.timing_label, dispatch)

    return finalize_result(
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
