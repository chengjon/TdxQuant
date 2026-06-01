## Why

PingAn ordinary buy/sell and submit-once paths now use an internal order execution seam. `TdxTradeManager.pingan.confirm_current(...)` is also part of D-07, but it is not an order submission flow: it advances the currently visible confirmation dialog and may close a result dialog. It has no code/price/quantity request context and must not be forced into the order-specific seam.

The next D-07 hardening step is to extract a confirm-current-specific internal seam that preserves the existing confirm flow while centralizing the same lifecycle rule: gate before UI side effects, capture timing around dispatch, and attach/finalize manager metadata consistently.

## What Changes

- Add an internal confirm-current execution request and seam for `TdxTradeManager.pingan.confirm_current(...)`.
- Route confirm-current through that seam after building the existing boundary risk gate and before UI lookup/click dispatch.
- Preserve current public manager contract, result shape, owner-lock/broker-readiness rejection behavior, timing label, metadata, safety data, and artifact behavior.
- Add a focused manager test proving confirm-current delegates to the seam and does not invoke UI lookup before the seam dispatch callback.
- Update `FUNCTION_TREE.md` D-07 evidence with the confirm-current seam proof and explicit boundaries.

## Non-Goals

- No reuse of the order-specific `PingAnExecutionRequest` for confirm-current.
- No new public CLI, task, catalog, or API surface.
- No change to dialog lookup, Win32/UIA click behavior, result-dialog close behavior, or artifact schemas.
- No live broker readiness, production trading readiness, or manual acceptance claim.

## Modified Capability

- `tdx-desktop-trading-management`

