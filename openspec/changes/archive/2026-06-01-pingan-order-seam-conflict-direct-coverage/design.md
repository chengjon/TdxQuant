## Context

The order seam handles four branch families:

- execute and dispatch,
- skip duplicate,
- reject submission-key conflict,
- reject failed risk/lifecycle/broker gate.

Direct coverage exists for all but submission-key conflict. This is a characterization coverage slice: the seam already supports the branch, but the branch contract should be pinned directly because buy/sell/submit-once now depend on the seam.

## Goals

- Test `reject_conflict` at the `execute_pingan_order` function boundary.
- Assert desktop dispatch is not called.
- Assert the conflict result builder receives the idempotency payload.
- Assert finalize receives `risk_gate.passed=false`, `risk_gate.rejection_reason`, `max_price`, and normalized request context.

## Non-Goals

- Do not change seam behavior unless the characterization test exposes an existing mismatch.
- Do not add public commands or runtime artifacts.
- Do not add generic workflow infrastructure.

## Compatibility

This is intended to be test-only hardening plus registry/spec evidence. Public runtime behavior remains unchanged.

## Validation

- Run focused PingAn trade execution tests.
- Run focused PingAn manager/gateway suite to verify no seam regression.
- Run OpenSpec validation, diff check, and FUNCTION_TREE registry validation.

