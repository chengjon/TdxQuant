# PingAn Order Dispatch Runner Kwargs

## Why

D-08 order execution already has an internal execution seam and `PingAnOrderDispatchOptions` for profile-derived desktop runner kwargs. The manager order callsites still choose between `base_kwargs(...)` and `fast_kwargs(...)` directly, so the fast/base kwargs selection remains spread across buy/sell/submit-once routing.

Adding one internal runner-kwargs selector keeps the dispatch option object responsible for the kwargs shape while preserving manager ownership of the actual desktop runner selection.

## What Changes

- Add `PingAnOrderDispatchOptions.runner_kwargs(..., fast_inputs=...)`.
- Keep `base_kwargs(...)` and `fast_kwargs(...)` for compatibility.
- Route buy/sell/submit-once manager callsites through `runner_kwargs(...)`.
- Add focused tests proving `runner_kwargs(...)` preserves base and fast kwargs shapes.
- Register the D-08 evidence and boundary in `FUNCTION_TREE.md`.

## Non-Goals

- No public CLI, task, catalog, API, or result schema changes.
- No change to `run_pingan_buy_fast`, `run_pingan_sell_fast`, HID/UIA behavior, artifact schemas, state paths, ledger paths, or audit schemas.
- No workflow builder, desktop primitive extraction, broker readiness claim, live acceptance claim, or production trading readiness claim.

## Modified Capability

- `tdx-desktop-trading-management`
