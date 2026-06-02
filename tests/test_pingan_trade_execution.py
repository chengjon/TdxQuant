from __future__ import annotations

import unittest

from tdxquant.models import ErrorCode, Result
from tdxquant.trade.pingan_execution import (
    PingAnConfirmCurrentDispatchContext,
    PingAnConfirmCurrentExecutionHandlers,
    PingAnConfirmCurrentExecutionRequest,
    PingAnConfirmCurrentRejectionContext,
    PingAnExecutionRequest,
    PingAnOrderExecutionHandlers,
    PingAnOrderResultContext,
    build_pingan_confirm_current_dispatch_result,
    build_pingan_confirm_current_boundary_rejection_result,
    build_pingan_order_duplicate_submission_result,
    build_pingan_order_risk_rejection_result,
    build_pingan_order_submission_key_conflict_result,
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

    def test_execute_pingan_order_rejects_conflict_without_desktop_dispatch(self) -> None:
        request = self._request()
        idempotency = {
            "decision": "reject_conflict",
            "submission_key": "submit-once-001",
            "conflict_reason": "submission_key reused with different payload",
        }
        calls: list[str] = []
        captured_conflict: dict[str, object] = {}

        def finalize_result(result: Result, **kwargs: object) -> Result:
            return Result(ok=result.ok, code=result.code, message=result.message, data={"finalized": kwargs})

        result = execute_pingan_order(
            request,
            idempotency=idempotency,
            risk_gate={"passed": True, "checks": ["max_price"]},
            dispatch=lambda: calls.append("dispatch") or Result(ok=True, code=ErrorCode.OK, message="ok"),
            build_duplicate_submission_result=lambda _prior_row: Result(
                ok=True,
                code=ErrorCode.OK,
                message="duplicate",
            ),
            build_submission_key_conflict_result=lambda conflict_idempotency: captured_conflict.update(
                conflict_idempotency
            )
            or Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="conflict rejected",
            ),
            build_trade_risk_rejection_result=lambda _risk_gate: Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="risk",
            ),
            finalize_result=finalize_result,
            capture_timing=lambda _label, runner: (runner(), {}),
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.message, "conflict rejected")
        self.assertEqual(calls, [])
        self.assertEqual(captured_conflict, idempotency)
        finalized = result.data["finalized"]
        self.assertEqual(finalized["risk_gate"]["passed"], False)
        self.assertEqual(finalized["risk_gate"]["max_price"], 10.50)
        self.assertEqual(finalized["risk_gate"]["rejection_reason"], idempotency["conflict_reason"])
        self.assertEqual(finalized["idempotency"], idempotency)
        self.assertEqual(finalized["request_context"], {"code": "000001", "price": "10.00", "quantity": 100})
        self.assertEqual(finalized["timing"], {})

    def test_execute_pingan_order_accepts_handler_bundle(self) -> None:
        request = self._request()
        handlers = PingAnOrderExecutionHandlers(
            build_duplicate_submission_result=lambda _prior_row: Result(
                ok=True,
                code=ErrorCode.OK,
                message="duplicate",
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
            finalize_result=lambda result, **kwargs: Result(
                ok=result.ok,
                code=result.code,
                message=result.message,
                data={"finalized": kwargs},
            ),
        )

        result = execute_pingan_order(
            request,
            idempotency={"decision": "execute"},
            risk_gate={"passed": True, "checks": ["max_price"]},
            dispatch=lambda: Result(
                ok=True,
                code=ErrorCode.OK,
                message="ok",
                data={"result_dialog": {"contract_no": "B001"}},
            ),
            handlers=handlers,
            capture_timing=lambda _label, runner: (runner(), {"manager_call": {"elapsed_ms": 1.0}}),
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.data["finalized"]["method"], "buy_submit_once")
        self.assertEqual(result.data["finalized"]["submission_key"], "submit-once-001")
        self.assertEqual(result.data["finalized"]["request_context"], {"code": "000001", "price": "10.00", "quantity": 100})

    def _order_result_context(self) -> PingAnOrderResultContext:
        return PingAnOrderResultContext(code="000001", price="10.00", quantity=100)

    def test_build_pingan_order_risk_rejection_result_uses_order_context(self) -> None:
        result = build_pingan_order_risk_rejection_result(
            {
                "passed": False,
                "rejection_reason": "requested price exceeds max_price",
            },
            context=self._order_result_context(),
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(result.message, "requested price exceeds max_price")
        self.assertEqual(result.data["input"], {"code": "000001", "price": "10.00", "quantity": 100})
        self.assertEqual(result.next_action, "Adjust the order request or trade safety controls, then retry.")

    def test_build_pingan_order_submission_key_conflict_result_uses_order_context(self) -> None:
        result = build_pingan_order_submission_key_conflict_result(
            {"conflict_reason": "submission_key reused with different payload"},
            context=self._order_result_context(),
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(result.message, "submission_key reused with different payload")
        self.assertEqual(result.data["input"], {"code": "000001", "price": "10.00", "quantity": 100})
        self.assertEqual(result.next_action, "Use a new submission_key for a new desktop trade attempt.")

    def test_build_pingan_order_duplicate_submission_result_marks_replayed_outcome(self) -> None:
        result = build_pingan_order_duplicate_submission_result(
            {
                "result": {
                    "ok": True,
                    "code": ErrorCode.OK.value,
                    "message": "submitted",
                    "input": {"code": "000001"},
                    "result_dialog": {"contract_no": "B001"},
                    "warnings": ["existing warning"],
                }
            }
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.code, ErrorCode.OK)
        self.assertEqual(result.message, "submitted")
        self.assertEqual(result.data["input"], {"code": "000001"})
        self.assertEqual(result.data["result_dialog"], {"contract_no": "B001"})
        self.assertEqual(
            result.warnings,
            ["existing warning", "duplicate submission_key skipped; returning prior outcome"],
        )

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

    def test_execute_pingan_confirm_current_accepts_handler_bundle(self) -> None:
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

        handlers = PingAnConfirmCurrentExecutionHandlers(
            build_rejected_result=lambda _risk_gate: Result(
                ok=False,
                code=ErrorCode.INVALID_REQUEST,
                message="rejected",
            ),
            attach_metadata=lambda result, _timing: calls.append("metadata") or result,
            attach_safety_metadata=lambda result, _risk_gate, _idempotency, _side_effect_level: calls.append("safety")
            or result,
            finalize_result=lambda result, **kwargs: finalized.update(kwargs)
            or Result(ok=result.ok, code=result.code, message=result.message, data={"finalized": kwargs}),
        )

        result = execute_pingan_confirm_current(
            request,
            risk_gate={"passed": True, "checks": ["confirm_boundary"]},
            dispatch=dispatch,
            handlers=handlers,
            capture_timing=lambda label, runner: calls.append(label) or (runner(), {"manager_call": {"elapsed_ms": 3.0}}),
        )

        self.assertTrue(result.ok)
        self.assertEqual(calls, ["pingan.confirm_current", "dispatch"])
        self.assertEqual(finalized["method"], "confirm_current")
        self.assertEqual(finalized["timing"], {"manager_call": {"elapsed_ms": 3.0}})
        self.assertTrue(finalized["risk_gate"]["passed"])
        self.assertEqual(finalized["idempotency"]["decision"], "not_applicable")
        self.assertIsNone(finalized["submission_key"])
        self.assertIsNone(finalized["request_context"])

    def _confirm_rejection_context(self):
        return PingAnConfirmCurrentRejectionContext(
            close_result_dialog=True,
            dialog_lookup_mode="uia",
            confirm_timeout=3.0,
            result_timeout=2.0,
            result_close_pre_delay=0.1,
            lifecycle_statefile_path="/tmp/pingan-lifecycle.json",
            lifecycle_owner_token="owner-token",
            lifecycle_stale_after_seconds=60.0,
            require_lifecycle_owner_lock=True,
            require_broker_readiness=False,
        )

    def test_build_pingan_confirm_current_boundary_rejection_result_for_owner_lock(self) -> None:
        result = build_pingan_confirm_current_boundary_rejection_result(
            {
                "passed": False,
                "lifecycle_owner_lock_required_status": {
                    "required": True,
                    "requirement_status": "failed",
                    "requirement_reason": "owner token mismatch",
                    "status": "not_acquired",
                },
            },
            context=self._confirm_rejection_context(),
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.INVALID_REQUEST)
        self.assertEqual(result.message, "stable trade confirm-current rejected by lifecycle owner-lock requirement")
        self.assertEqual(result.next_action, "Acquire the PingAn lifecycle owner lock and retry confirm-current.")
        self.assertEqual(result.data["input"]["boundary"], "confirm_current")
        self.assertEqual(result.data["input"]["lifecycle_owner_token"], "owner-token")
        confirm_current = result.data["confirm_current"]
        self.assertEqual(confirm_current["overall_status"], "failed")
        self.assertFalse(confirm_current["confirmation_advanced"])
        self.assertFalse(confirm_current["result_dialog_closed"])
        check = confirm_current["checks"][0]
        self.assertEqual(check["name"], "lifecycle_owner_lock_required")
        self.assertEqual(check["status"], "failed")
        self.assertTrue(check["critical"])
        self.assertEqual(check["summary"], "owner token mismatch")
        self.assertEqual(result.data["result_dialog"], {})

    def test_build_pingan_confirm_current_boundary_rejection_result_for_broker_readiness(self) -> None:
        result = build_pingan_confirm_current_boundary_rejection_result(
            {
                "passed": False,
                "broker_readiness_required_status": {
                    "required": True,
                    "requirement_status": "failed",
                    "requirement_reason": "broker window missing",
                    "broker_health": {
                        "code": ErrorCode.CONTROL_NOT_FOUND.value,
                        "next_action": "Bring Ping An to the foreground.",
                    },
                },
            },
            context=self._confirm_rejection_context(),
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.CONTROL_NOT_FOUND)
        self.assertEqual(result.message, "stable trade confirm-current rejected by broker readiness requirement")
        self.assertEqual(result.next_action, "Bring Ping An to the foreground.")
        self.assertTrue(result.data["input"]["require_lifecycle_owner_lock"])
        confirm_current = result.data["confirm_current"]
        check = confirm_current["checks"][0]
        self.assertEqual(check["name"], "broker_readiness_required")
        self.assertEqual(check["summary"], "broker window missing")
        self.assertEqual(check["recommended_action"], "Bring Ping An to the foreground.")

    def _confirm_dispatch_context(self):
        return PingAnConfirmCurrentDispatchContext(
            close_result_dialog=True,
            dialog_lookup_mode="uia",
            confirm_timeout=3.0,
            result_timeout=2.0,
            result_close_pre_delay=0.1,
        )

    def test_build_pingan_confirm_current_dispatch_result_for_lookup_failure(self) -> None:
        checks = [{"name": "confirm_lookup", "status": "failed", "summary": "confirm dialog missing"}]

        result = build_pingan_confirm_current_dispatch_result(
            context=self._confirm_dispatch_context(),
            ok=False,
            code=ErrorCode.CONTROL_NOT_FOUND,
            message="stable trade confirm-current could not locate the current confirm dialog",
            checks=checks,
            overall_status="failed",
            confirmation_advanced=False,
            result_dialog_closed=False,
            result_dialog_payload={},
            warnings=["confirm dialog missing"],
            next_action="Keep the current confirm dialog visible.",
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.code, ErrorCode.CONTROL_NOT_FOUND)
        self.assertEqual(result.message, "stable trade confirm-current could not locate the current confirm dialog")
        self.assertEqual(result.warnings, ["confirm dialog missing"])
        self.assertEqual(result.next_action, "Keep the current confirm dialog visible.")
        self.assertEqual(result.data["input"]["boundary"], "confirm_current")
        self.assertEqual(result.data["input"]["dialog_lookup_mode"], "uia")
        confirm_current = result.data["confirm_current"]
        self.assertEqual(confirm_current["overall_status"], "failed")
        self.assertFalse(confirm_current["confirmation_advanced"])
        self.assertFalse(confirm_current["result_dialog_closed"])
        self.assertEqual(confirm_current["checks"], checks)
        self.assertEqual(result.data["result_dialog"], {})

    def test_build_pingan_confirm_current_dispatch_result_for_advanced_warning(self) -> None:
        checks = [{"name": "result_dialog_lookup", "status": "warning", "summary": "result dialog missing"}]
        result_dialog_payload = {"contract_no": "B202606010001", "lookup_mode": "uia"}

        result = build_pingan_confirm_current_dispatch_result(
            context=self._confirm_dispatch_context(),
            ok=True,
            code=ErrorCode.OK,
            message="stable trade confirm-current completed with warnings",
            checks=checks,
            overall_status="warning",
            confirmation_advanced=True,
            result_dialog_closed=False,
            result_dialog_payload=result_dialog_payload,
            warnings=["result dialog missing"],
            next_action="Verify the order outcome manually.",
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.code, ErrorCode.OK)
        self.assertEqual(result.data["input"]["close_result_dialog"], True)
        confirm_current = result.data["confirm_current"]
        self.assertEqual(confirm_current["overall_status"], "warning")
        self.assertTrue(confirm_current["confirmation_advanced"])
        self.assertFalse(confirm_current["result_dialog_closed"])
        self.assertEqual(confirm_current["requested"]["result_close_pre_delay"], 0.1)
        self.assertEqual(result.data["result_dialog"], result_dialog_payload)
