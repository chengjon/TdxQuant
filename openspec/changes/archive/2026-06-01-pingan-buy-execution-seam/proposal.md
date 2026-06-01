## Why

`TdxTradeManager.pingan.buy_submit_once` and `sell_submit_once` already route through the internal `PingAnExecutionRequest` / `execute_pingan_order` seam. The ordinary PingAn `buy` path still keeps the same idempotency, risk gate, lifecycle/broker readiness, desktop dispatch, and finalize/audit flow inline in `tdxquant/trade/manager.py`.

This keeps D-07 implemented, but leaves the ordinary buy workflow outside the seam that now owns PingAn execution policy. Aligning `buy` first is the smallest D-07 hardening step because it is closest to the already migrated buy submit-once path and does not require changing public commands or desktop automation primitives.

## What Changes

- Route `TdxTradeManager.pingan.buy(...)` through the existing internal PingAn execution seam.
- Preserve the existing public manager contract, public result shape, idempotency decisions, risk/lifecycle/broker readiness gates, timing label, audit metadata, and artifact behavior.
- Add a focused manager test proving ordinary buy delegates to the seam and does not invoke the desktop primitive before the seam dispatch callback.
- Update `FUNCTION_TREE.md` D-07 evidence with the new seam-alignment proof and explicit boundaries.

## Non-Goals

- No new public CLI, task, catalog, or API surface.
- No migration of `TdxTradeManager.pingan.sell(...)` or `confirm_current(...)` in this change.
- No new `run_pingan_buy` desktop primitive and no change to `run_pingan_buy_fast`.
- No live broker readiness, production trading readiness, or manual acceptance claim.

## Modified Capability

- `tdx-desktop-trading-management`

