from __future__ import annotations

import unittest

from tdxquant.models import ErrorCode, Result
from tdxquant.trade.pingan_execution import (
    PingAnConfirmCurrentExecutionRequest,
    PingAnExecutionRequest,
    execute_pingan_confirm_current,
    execute_pingan_order,
)


class PingAnTradeExecutionTests(unittest.TestCase):
    def _request(self) -> PingAnExecutionRequest:
        return PingAnExecutionRequest(
            method="buy_submit_once",
            timing_label="pingan.buy_submit_once",
            code="000001",
            price="10.00",
            quantity=100,
            submission_key="submit-once-001",
            max_price=10.50,
            profile_options={"profile": "submit_once"},
        )

    def test_execute_pingan_order_dispatches_and_finalizes_successful_request(self) -> None:
        request = self._request()
        calls: list[str] = []
        finalized: dict[str, object] = {}
        dispatch_result = Result(
            ok=True,
            code=ErrorCode.OK,
            message="ok",
            data={"result_dialog": {"contract_no": "B001"}},
        )

        def dispatch() -> Result:
            calls.append("dispatch")
            return dispatch_result

        def capture_timing(label: str, runner):
            calls.append(label)
            return runner(), {"manager_call": {"elapsed_ms": 1.0}}

        def finalize_result(result: Result, **kwargs: object) -> Result:
            finalized.update(kwargs)
            return Result(ok=result.ok, code=result.code, message=result.message, data={"finalized": kwargs})

        result = execute_pingan_order(
            request,
            idempotency={"decision": "execute"},
            risk_gate={"passed": True, "checks": ["max_price"]},
            dispatch=dispatch,
            build_duplicate_submission_result=lambda _prior_row: Result(ok=True, code=ErrorCode.OK, message="duplicate"),
            build_submission_key_conflict_result=lambda _idempotency: Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="conflict",
            ),
            build_trade_risk_rejection_result=lambda _risk_gate: Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="risk",
            ),
            finalize_result=finalize_result,
            capture_timing=capture_timing,
        )

        self.assertTrue(result.ok)
        self.assertEqual(calls, ["pingan.buy_submit_once", "dispatch"])
        self.assertEqual(finalized["broker"], "pingan")
        self.assertEqual(finalized["method"], "buy_submit_once")
        self.assertEqual(finalized["submission_key"], "submit-once-001")
        self.assertEqual(finalized["risk_gate"], {"passed": True, "checks": ["max_price"]})
        self.assertEqual(finalized["idempotency"], {"decision": "execute"})
        self.assertEqual(finalized["request_context"], {"code": "000001", "price": "10.00", "quantity": 100})
        self.assertEqual(finalized["timing"], {"manager_call": {"elapsed_ms": 1.0}})

    def test_execute_pingan_order_rejects_failed_gate_without_desktop_dispatch(self) -> None:
        request = self._request()
        calls: list[str] = []
        risk_gate = {"passed": False, "checks": ["max_price"], "rejection_reason": "price_above_max"}

        def finalize_result(result: Result, **kwargs: object) -> Result:
            return Result(ok=result.ok, code=result.code, message=result.message, data={"finalized": kwargs})

        result = execute_pingan_order(
            request,
            idempotency={"decision": "execute"},
            risk_gate=risk_gate,
            dispatch=lambda: calls.append("dispatch") or Result(ok=True, code=ErrorCode.OK, message="ok"),
            build_duplicate_submission_result=lambda _prior_row: Result(ok=True, code=ErrorCode.OK, message="duplicate"),
            build_submission_key_conflict_result=lambda _idempotency: Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="conflict",
            ),
            build_trade_risk_rejection_result=lambda _risk_gate: Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="risk rejected",
            ),
            finalize_result=finalize_result,
            capture_timing=lambda _label, runner: (runner(), {}),
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.message, "risk rejected")
        self.assertEqual(calls, [])
        self.assertEqual(result.data["finalized"]["risk_gate"], risk_gate)
        self.assertEqual(result.data["finalized"]["timing"], {})

    def test_execute_pingan_order_skips_duplicate_without_desktop_dispatch(self) -> None:
        request = self._request()
        prior_row = {"submission_key": "submit-once-001", "status": "confirmed"}
        calls: list[str] = []

        def finalize_result(result: Result, **kwargs: object) -> Result:
            return Result(ok=result.ok, code=result.code, message=result.message, data={"finalized": kwargs})

        result = execute_pingan_order(
            request,
            idempotency={"decision": "skip_duplicate", "prior_row": prior_row},
            risk_gate={"passed": True, "checks": ["max_price"]},
            dispatch=lambda: calls.append("dispatch") or Result(ok=True, code=ErrorCode.OK, message="ok"),
            build_duplicate_submission_result=lambda row: Result(
                ok=True,
                code=ErrorCode.OK,
                message=f"duplicate {row['submission_key']}",
            ),
            build_submission_key_conflict_result=lambda _idempotency: Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="conflict",
            ),
            build_trade_risk_rejection_result=lambda _risk_gate: Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="risk",
            ),
            finalize_result=finalize_result,
            capture_timing=lambda _label, runner: (runner(), {}),
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.message, "duplicate submit-once-001")
        self.assertEqual(calls, [])
        self.assertEqual(result.data["finalized"]["risk_gate"]["passed"], True)
        self.assertIsNone(result.data["finalized"]["risk_gate"]["requested_price"])

    def _confirm_request(self):
        return PingAnConfirmCurrentExecutionRequest(
            method="confirm_current",
            timing_label="pingan.confirm_current",
            profile_options={"profile": "balanced"},
        )

    def test_execute_pingan_confirm_current_rejects_failed_gate_without_dispatch(self) -> None:
        request = self._confirm_request()
        calls: list[str] = []
        attached_safety: dict[str, object] = {}

        result = execute_pingan_confirm_current(
            request,
            risk_gate={"passed": False, "checks": ["owner_lock"], "rejection_reason": "owner_lock_missing"},
            dispatch=lambda: calls.append("dispatch") or Result(ok=True, code=ErrorCode.OK, message="advanced"),
            build_rejected_result=lambda _risk_gate: Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="rejected",
                data={},
            ),
            attach_metadata=lambda result, timing: calls.append(f"metadata:{timing}") or result,
            attach_safety_metadata=lambda result, risk_gate, idempotency, side_effect_level: attached_safety.update(
                {"risk_gate": risk_gate, "idempotency": idempotency, "side_effect_level": side_effect_level}
            )
            or result,
            finalize_result=lambda result, **_kwargs: calls.append("finalize") or result,
            capture_timing=lambda label, runner: calls.append(label) or (runner(), {}),
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.message, "rejected")
        self.assertEqual(calls, ["metadata:{}"])
        self.assertFalse(attached_safety["risk_gate"]["passed"])
        self.assertEqual(attached_safety["idempotency"]["decision"], "not_applicable")
        self.assertEqual(attached_safety["side_effect_level"], "none")

    def test_execute_pingan_confirm_current_attaches_metadata_without_finalize_when_not_advanced(self) -> None:
        request = self._confirm_request()
        calls: list[str] = []
        attached_metadata: dict[str, object] = {}
        attached_safety: dict[str, object] = {}

        def dispatch() -> Result:
            calls.append("dispatch")
            return Result(
                ok=False,
                code=ErrorCode.CONTROL_NOT_FOUND,
                message="confirm dialog not found",
                data={"confirm_current": {"confirmation_advanced": False}},
            )

        result = execute_pingan_confirm_current(
            request,
            risk_gate={"passed": True, "checks": ["confirm_boundary"]},
            dispatch=dispatch,
            build_rejected_result=lambda _risk_gate: Result(ok=False, code=ErrorCode.INVALID_REQUEST, message="rejected"),
            attach_metadata=lambda result, timing: attached_metadata.update({"timing": timing}) or result,
            attach_safety_metadata=lambda result, risk_gate, idempotency, side_effect_level: attached_safety.update(
                {"risk_gate": risk_gate, "idempotency": idempotency, "side_effect_level": side_effect_level}
            )
            or result,
            finalize_result=lambda result, **_kwargs: calls.append("finalize") or result,
            capture_timing=lambda label, runner: calls.append(label) or (runner(), {"manager_call": {"elapsed_ms": 1.0}}),
        )

        self.assertFalse(result.ok)
        self.assertEqual(calls, ["pingan.confirm_current", "dispatch"])
        self.assertEqual(attached_metadata["timing"], {"manager_call": {"elapsed_ms": 1.0}})
        self.assertTrue(attached_safety["risk_gate"]["passed"])
        self.assertEqual(attached_safety["idempotency"]["decision"], "not_applicable")
        self.assertIsNone(attached_safety["side_effect_level"])

    def test_execute_pingan_confirm_current_finalizes_when_confirmation_advanced(self) -> None:
        request = self._confirm_request()
        calls: list[str] = []
        finalized: dict[str, object] = {}

        def dispatch() -> Result:
            calls.append("dispatch")
            return Result(
                ok=True,
                code=ErrorCode.OK,
                message="advanced",
                data={"confirm_current": {"confirmation_advanced": True}},
            )

        result = execute_pingan_confirm_current(
            request,
            risk_gate={"passed": True, "checks": ["confirm_boundary"]},
            dispatch=dispatch,
            build_rejected_result=lambda _risk_gate: Result(ok=False, code=ErrorCode.INVALID_REQUEST, message="rejected"),
            attach_metadata=lambda result, _timing: calls.append("metadata") or result,
            attach_safety_metadata=lambda result, _risk_gate, _idempotency, _side_effect_level: calls.append("safety")
            or result,
            finalize_result=lambda result, **kwargs: finalized.update(kwargs)
            or Result(ok=result.ok, code=result.code, message=result.message, data={"finalized": kwargs}),
            capture_timing=lambda label, runner: calls.append(label) or (runner(), {"manager_call": {"elapsed_ms": 2.0}}),
        )

        self.assertTrue(result.ok)
        self.assertEqual(calls, ["pingan.confirm_current", "dispatch"])
        self.assertEqual(finalized["method"], "confirm_current")
        self.assertEqual(finalized["timing"], {"manager_call": {"elapsed_ms": 2.0}})
        self.assertEqual(finalized["idempotency"]["decision"], "not_applicable")
        self.assertIsNone(finalized["submission_key"])
        self.assertIsNone(finalized["request_context"])
