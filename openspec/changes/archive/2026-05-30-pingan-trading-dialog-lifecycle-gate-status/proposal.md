## Why

The PingAn promotion plan now has provider/broker ownership and safety preflight evidence, but D-07/D-08 still need desktop lifecycle evidence before any implemented-status transition. Existing dialog readiness checks already cover confirm/result dialog lookup; this change gives that evidence a stable gate-status shape and keeps the remaining lifecycle gaps explicit.

## What Changes

- Add a readonly `desktop_lifecycle_gate_status` payload to `TdxTradeManager.pingan.dialog_readiness`.
- Summarize confirm dialog lookup, result dialog lookup, result confirm-button lookup, timeout settings, lookup mode, and declared process/window ownership inputs.
- Explicitly mark the gate as partial when exception popup handling, retry policy, audit evidence, or acceptance evidence are still outside this check.
- Update D-07/D-08 FUNCTION_TREE evidence without moving either node from `[部分实现]`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-desktop-trading-dialog-readiness`: require dialog readiness to expose readonly desktop lifecycle gate status.
- `tdx-desktop-trading-safety`: register lifecycle gate status as partial promotion evidence only.
- `tdx-function-tree-registry`: require D-07/D-08 to record lifecycle status evidence without claiming implemented status.

## Impact

- `tdxquant/trade/manager.py`
- `tests/test_trade_manager.py`
- `FUNCTION_TREE.md`
- OpenSpec specs for dialog readiness, desktop trading safety, and FUNCTION_TREE registry
