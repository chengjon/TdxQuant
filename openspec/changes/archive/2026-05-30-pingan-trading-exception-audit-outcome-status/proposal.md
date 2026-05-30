## Why

D-07/D-08 promotion gates require outcome evidence for success, failure, rejection, and exception paths. The current audit status resolver declares `exception` as a required gate status, but finalized PingAn results cannot currently produce a distinct `exception` audit status.

## What Changes

- Recognize explicitly marked desktop exception results in the finalized PingAn trade audit status resolver.
- Persist those finalized results with `trade_audit.status=exception` and `trade_audit_gate_status.covered_audit_status=exception`.
- Add focused tests for an exception-marked finalized PingAn buy result.
- Register the evidence in `FUNCTION_TREE.md` while keeping D-07/D-08 `[部分实现]`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-desktop-trading-audit`: require finalized PingAn exception-marked results to expose distinct exception audit gate status.
- `tdx-desktop-trading-safety`: keep exception audit outcome evidence as partial promotion evidence only.
- `tdx-function-tree-registry`: require D-07/D-08 to record exception audit evidence without claiming implemented status.

## Impact

- `tdxquant/trade/context.py`
- `tests/test_trade_manager.py`
- `FUNCTION_TREE.md`
- OpenSpec specs for desktop trading audit, desktop trading safety, and FUNCTION_TREE registry

