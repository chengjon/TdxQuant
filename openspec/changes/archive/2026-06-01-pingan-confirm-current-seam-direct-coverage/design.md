## Context

The confirm-current seam differs from the order seam because confirm-current does not carry code, price, quantity, or submission-key/idempotency ledger semantics. It coordinates gate-before-dispatch, timing, metadata attachment, and finalize behavior around the existing confirm dialog dispatch callback.

The current manager delegation test proves that `TdxTradeManager.pingan.confirm_current(...)` reaches the seam before UI lookup. This change adds direct seam tests so future refactors can safely move more manager logic behind the seam without losing branch behavior.

## Goals

- Exercise `execute_pingan_confirm_current` directly, without manager or desktop UI mocks.
- Keep tests local to [tests/test_pingan_trade_execution.py](/opt/iflow/TdxQuant/tests/test_pingan_trade_execution.py).
- Assert only stable seam contracts: dispatch/no-dispatch, metadata callback usage, finalize callback usage, timing label, idempotency marker, side-effect level, and null request context.

## Non-Goals

- Do not move additional code from manager into the seam.
- Do not add new result schemas.
- Do not change manager behavior or public APIs.

## Compatibility

This is a test-only hardening slice. Existing runtime behavior and public interfaces stay unchanged.

## Validation

- Run the new direct seam tests before implementation to confirm missing coverage/imports fail.
- Run the focused PingAn trade execution/manager/gateway suite.
- Run OpenSpec validation, diff check, and FUNCTION_TREE registry validation.

