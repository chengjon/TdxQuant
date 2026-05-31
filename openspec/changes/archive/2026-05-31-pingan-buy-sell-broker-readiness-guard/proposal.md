# PingAn Buy/Sell Broker Readiness Guard

## Summary

Add an opt-in PingAn broker runtime readiness guard to the stable `buy` and `sell` desktop trading paths. When required and the PingAn broker health check fails, the manager rejects before dispatching buy/sell desktop UI automation.

## Motivation

D-07 already has partial evidence for buy/sell, confirm-current, lifecycle owner-lock, and confirm-current broker readiness guard behavior. The current buy/sell paths can be protected by lifecycle owner-lock checks, but they do not yet have the same opt-in broker runtime health requirement that was added to confirm-current. This leaves a gap between readiness diagnostics and the highest-risk buy/sell desktop execution paths.

## Scope

- Add `require_broker_readiness` to `TdxTradeManager.pingan.buy(...)` and `TdxTradeManager.pingan.sell(...)`.
- Reject before `run_pingan_buy_fast(...)` or `run_pingan_sell_fast(...)` when the guard is required and broker health is not OK.
- Forward the option through task buy/sell entrypoints.
- Expose the option on direct trade buy/sell CLI and task trade-buy/trade-sell CLI entrypoints.
- Register the evidence and boundary on D-07 in `FUNCTION_TREE.md`.

## Non-Goals

- No change to submit-once, submit-ready, confirm-current, or exception-popup behavior.
- No retry, recovery, resubmission, restart/backoff, supervisor, process ownership, or daemon lifecycle implementation.
- No automatic promotion of D-07 to `[已实现]`.
- No claim that broker readiness passing proves production trading readiness or live acceptance.
