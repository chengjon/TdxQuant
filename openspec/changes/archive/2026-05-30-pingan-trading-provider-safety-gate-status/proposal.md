## Why

D-07 and D-08 have a registered promotion plan, but the first real gate still needs implementation evidence that is more concrete than catalog parsing. A readonly preflight gate status gives maintainers a stable place to inspect provider/broker ownership and safety controls before any later lifecycle, audit, or live acceptance work.

## What Changes

- Add a normalized PingAn promotion gate status to the existing readonly `trade preflight` result.
- Report provider/broker ownership for the PingAn desktop broker path, including broker identity, adapter/manager ownership, supported broker list, and non-execution boundary.
- Report safety gate readiness for `max_price`, `submission_key`/idempotency, risk-gate result, and explicit approval semantics.
- Update D-07/D-08 FUNCTION_TREE evidence while keeping both nodes `[部分实现]`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-desktop-trading-safety`: require readonly preflight output to expose provider/broker ownership and safety gate status for PingAn promotion evidence.
- `tdx-function-tree-registry`: require D-07/D-08 to record this gate as partial promotion evidence without claiming implemented status.

## Impact

- `tdxquant/trade/manager.py`
- `tests/test_trade_manager.py`
- `FUNCTION_TREE.md`
- OpenSpec specs for desktop trading safety and function tree registry
