## Why

`TdxTradeManager.pingan.buy(...)`, `buy_submit_once(...)`, and `sell_submit_once(...)` now route through the internal `PingAnExecutionRequest` / `execute_pingan_order` seam. The ordinary PingAn `sell` path still keeps equivalent idempotency, risk gate, lifecycle/broker readiness, desktop dispatch, and finalize/audit policy inline in `tdxquant/trade/manager.py`.

Migrating ordinary `sell` is the next narrow D-07 hardening step: it aligns the buy/sell order paths behind the same internal execution seam without changing public caller behavior.

## What Changes

- Route `TdxTradeManager.pingan.sell(...)` through the existing internal PingAn execution seam.
- Preserve the existing public manager contract, result shape, idempotency decisions, risk/lifecycle/broker readiness gates, timing label, audit metadata, and artifact behavior.
- Add a focused manager test proving ordinary sell delegates to the seam and does not invoke the desktop primitive before the seam dispatch callback.
- Update `FUNCTION_TREE.md` D-07 evidence with the new sell seam-alignment proof and explicit boundaries.

## Non-Goals

- No new public CLI, task, catalog, or API surface.
- No migration of `TdxTradeManager.pingan.confirm_current(...)` in this change.
- No new `run_pingan_sell` desktop primitive and no change to `run_pingan_sell_fast`.
- No live broker readiness, production trading readiness, or manual acceptance claim.

## Modified Capability

- `tdx-desktop-trading-management`

