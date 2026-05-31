# PingAn Submit-Once Broker Readiness Guard

## Why

D-08 already registers PingAn submit-once as a partial feature with explicit buy/sell side boundaries and catalog discovery coverage. The normal buy/sell paths now have an opt-in broker runtime readiness guard, but `buy_submit_once` / `sell_submit_once` still lack the same pre-desktop-dispatch guard. Because submit-once is also a side-effecting desktop execution path, it should be able to reject before UI automation when broker runtime health is explicitly required and unavailable.

## What Changes

- Add `require_broker_readiness` to `TdxTradeManager.pingan.buy_submit_once(...)` and `sell_submit_once(...)`.
- Reject before submit-once desktop automation when the guard is required and PingAn broker health fails.
- Forward the option through `TdxTaskManager.trade_submit_once(...)`.
- Expose and forward the option through `trade submit-once --require-broker-readiness` and `task trade-submit-once --require-broker-readiness`.
- Preserve the default behavior when the guard is not requested.
- Update D-08 in `FUNCTION_TREE.md` with explicit evidence and boundary text while keeping `[部分实现]`.

## Non-Goals

- No changes to regular buy/sell, submit-ready, confirm-current, or exception-popup behavior.
- No daemon lifecycle control, long-running supervisor, restart/backoff, retry, recovery, resubmission, process ownership, or statefile ownership implementation.
- No automatic promotion of D-08 to `[已实现]`.
- No claim that broker readiness passing proves production trading readiness or live/manual acceptance.
