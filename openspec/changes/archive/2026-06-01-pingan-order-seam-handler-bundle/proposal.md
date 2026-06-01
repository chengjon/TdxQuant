## Why

`execute_pingan_order` is now shared by ordinary buy, ordinary sell, buy submit-once, and sell submit-once. Each manager callsite currently repeats the same callback bundle:

- duplicate submission result builder,
- submission-key conflict result builder,
- trade risk rejection result builder,
- finalize result callback.

That repetition makes the manager methods noisy and makes future seam changes harder to review. A small handler object can keep those callbacks grouped as one internal seam dependency while preserving the existing public manager behavior.

## What Changes

- Add `PingAnOrderExecutionHandlers` in `tdxquant/trade/pingan_execution.py`.
- Let `execute_pingan_order` accept `handlers=` while keeping existing callback parameters for compatibility.
- Add a `TdxTradeManager` helper that builds the handler bundle for a normalized order context.
- Route buy/sell/submit-once manager callsites through the handler bundle.
- Update `FUNCTION_TREE.md` D-08 evidence and boundary.

## Non-Goals

- No public CLI, task, catalog, or API changes.
- No behavior change for idempotency, risk/lifecycle/broker gates, desktop dispatch, finalize/audit, or artifact writes.
- No changes to desktop primitives or runtime state paths.
- No live broker readiness, production trading readiness, or manual acceptance claim.

## Modified Capability

- `tdx-desktop-trading-management`

