## Context

The prior `pingan-trading-implemented-promotion-plan` change defined the gate order for promoting D-07/D-08 to `[已实现]`: provider/broker ownership, safety gates, desktop lifecycle, audit evidence, acceptance gates, then status transition. The current code already has `trade preflight`, broker health/detection checks, `evaluate_trade_risk_gate`, and submission-key idempotency checks. The missing piece is a stable, normalized status object that ties those checks to the promotion plan without executing a trade.

## Goals / Non-Goals

**Goals:**

- Make `trade preflight` return a `promotion_gate_status` object with provider/broker ownership and safety gate readiness.
- Keep the gate readonly: no order submission, no task execution, no catalog dispatch, and no ledger/state/audit writes.
- Preserve D-07/D-08 as `[部分实现]` and use this as evidence for only the first promotion gate.

**Non-Goals:**

- Do not promote D-07/D-08 to `[已实现]`.
- Do not implement long-running lifecycle, result popup coverage, timeout/retry lifecycle ownership, or live/manual acceptance evidence.
- Do not add a new workflow builder or a new execution path.

## Decisions

- Attach the gate status to `TdxTradeManager.pingan.preflight` instead of introducing another command. Preflight already owns broker health, desktop detectability, risk-gate evaluation, idempotency checks, and HID readiness, so the status can reuse existing evidence and tests.
- Use explicit per-gate states instead of a single boolean. `max_price` can be `configured` or `missing`, `submission_key` can be `provided` or `missing`, and idempotency can still report `execute`, `skip_duplicate`, or `reject_conflict`.
- Treat explicit approval as `not_granted` in preflight. A live order still requires a later explicit execution command and environment approval; preflight must not imply execution approval.

## Risks / Trade-offs

- [Risk] Operators may mistake readiness metadata for live readiness. -> Include `execution_mode=readonly_preflight`, `dispatch_executed=false`, `order_submitted=false`, and explicit missing gates.
- [Risk] Existing preflight failures could hide gate status. -> Build the status from already-computed risk/idempotency data before returning the result so callers can inspect failed safety gates.
- [Risk] This only covers the first promotion gate. -> FUNCTION_TREE boundary stays partial and points to remaining lifecycle/audit/acceptance gates.
