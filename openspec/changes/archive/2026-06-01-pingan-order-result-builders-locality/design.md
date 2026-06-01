## Context

`execute_pingan_order` now owns the order seam decision flow and accepts `PingAnOrderExecutionHandlers`, but the concrete result builders used by those handlers remain private methods on `TdxTradeManager`.

The manager should assemble runtime dependencies and route desktop calls, while the PingAn execution module should own order execution result envelopes that are independent of manager instance state.

## Design

Introduce `PingAnOrderResultContext` in `tdxquant/trade/pingan_execution.py`:

- `code`
- `price`
- `quantity`

Add three pure builder helpers:

- `build_pingan_order_duplicate_submission_result(prior_row)`
- `build_pingan_order_submission_key_conflict_result(idempotency, context=...)`
- `build_pingan_order_risk_rejection_result(risk_gate, context=...)`

Update `TdxTradeManager._build_pingan_order_execution_handlers(...)` to call these helpers. Update submit-ready risk rejection to reuse the same risk rejection builder so the result shape has one owner.

The existing `PingAnOrderExecutionHandlers` contract stays in place, and legacy `execute_pingan_order` callback kwargs remain available.

## Non-Goals

- No behavior changes to buy/sell/submit-once/submit-ready.
- No CLI/task/catalog changes.
- No public API commitment for the new helpers beyond internal module usage and tests.
- No desktop automation, broker readiness, audit, idempotency, lifecycle, or live/manual acceptance expansion.
