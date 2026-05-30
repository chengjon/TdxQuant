## Why

D-07/D-08 now have distinct confirmed, rejected, and explicit exception audit evidence, but generic failed finalized results still only expose `covered_audit_status=failed` without explaining why the result was classified as failed. A stable classification signal makes failed outcome evidence auditable without implying exception popup handling or live acceptance.

## What Changes

- Add `audit_status_classification` to PingAn `trade_audit_gate_status`.
- Classify generic non-OK finalized results without explicit exception metadata as `source=generic_execution_failure`.
- Preserve existing replayed, rejected, confirmed, and explicit exception status behavior.
- Register the failed classification evidence in `FUNCTION_TREE.md` while keeping D-07/D-08 `[部分实现]`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-desktop-trading-audit`: require finalized PingAn audit gate status to include status classification details.
- `tdx-desktop-trading-safety`: register failed classification evidence as partial promotion evidence only.
- `tdx-function-tree-registry`: require D-07/D-08 to record failed classification evidence without claiming implemented status.

## Impact

- `tdxquant/trade/manager.py`
- `tests/test_trade_manager.py`
- `FUNCTION_TREE.md`
- OpenSpec specs for desktop trading audit, desktop trading safety, and FUNCTION_TREE registry

