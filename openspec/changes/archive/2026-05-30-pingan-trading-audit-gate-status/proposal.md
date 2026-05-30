## Why

D-07/D-08 promotion now has readonly provider/safety and dialog lifecycle gate evidence, but finalized trade paths still need a normalized way to show which audit artifacts were written for each outcome. Existing finalized workflows already write last-order state, order-event rows, optional submission ledgers, and immutable trade-audit artifacts; this change exposes those writes as explicit audit gate evidence.

## What Changes

- Add `trade_audit_gate_status` to finalized PingAn trade results that go through the standard `_finalize_result` persistence path.
- Summarize audit status, audit id, method, artifact paths, and whether state/event/ledger/audit artifacts were produced.
- Mark the gate as partial evidence because a single finalized result only proves its own audit outcome, not all success/failure/rejection/exception scenarios or live acceptance.
- Update D-07/D-08 FUNCTION_TREE evidence without moving either node from `[部分实现]`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-desktop-trading-audit`: require finalized workflows to expose normalized audit gate status.
- `tdx-desktop-trading-safety`: register audit gate status as partial promotion evidence only.
- `tdx-function-tree-registry`: require D-07/D-08 to record audit gate status evidence without claiming implemented status.

## Impact

- `tdxquant/trade/manager.py`
- `tests/test_trade_manager.py`
- `FUNCTION_TREE.md`
- OpenSpec specs for desktop trading audit, desktop trading safety, and FUNCTION_TREE registry
