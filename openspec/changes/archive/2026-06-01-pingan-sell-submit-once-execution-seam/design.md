## Context

`tdxquant.trade.pingan_execution` now owns the internal D-08 execution seam for `buy_submit_once`. The sell submit-once path still contains duplicated manager-side control flow for idempotency, safety/lifecycle/broker gates, desktop dispatch, and finalization. This is the next narrow migration step before considering broader D-07 buy/sell/confirm-current movement.

## Goals / Non-Goals

**Goals:**
- Delegate `sell_submit_once` through the existing internal PingAn execution seam.
- Keep `method=sell_submit_once` in manager/audit metadata.
- Keep desktop dispatch using `run_pingan_sell_fast`.
- Preserve existing idempotency, risk gate, broker readiness, lifecycle owner, and artifact behavior.
- Keep tests focused and limited to D-08 submit-once behavior.

**Non-Goals:**
- No new sell-specific desktop primitive.
- No migration of plain `buy`, plain `sell`, or `confirm_current`.
- No CLI/task/catalog changes.
- No change to live trading safety defaults or FUNCTION_TREE status.

## Decisions

- Reuse `PingAnExecutionRequest` and `execute_pingan_order` without adding a second seam. This proves the seam handles both submit-once sides.
- Keep manager-owned risk/idempotency/lifecycle/broker gate construction in place for this slice. The seam owns decision-to-dispatch/finalize flow; deeper extraction of gate construction can be a later slice.
- Use a routing compatibility test that patches `execute_pingan_order`; if the manager regresses to direct desktop dispatch, the test fails.

## Risks / Trade-offs

- The new seam could hide that sell still uses `run_pingan_sell_fast`. Mitigation: tests and FUNCTION_TREE boundary explicitly state the desktop primitive remains unchanged.
- Moving too much logic could change trade output. Mitigation: existing sell submit-once tests stay in the focused verification set.
