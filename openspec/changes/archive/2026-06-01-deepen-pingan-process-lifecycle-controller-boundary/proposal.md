## Why

PingAn process lifecycle control is implemented, but `lifecycle_process` still mixes owner-lock gate evaluation, recorded-PID guard decisions, process start/stop execution, and result-shape assembly in the trade manager path. A controller decision boundary makes the high-risk lifecycle path easier to test without changing real process execution behavior.

## What Changes

- Add a PingAn lifecycle controller boundary for `lifecycle_process` owner-gate and recorded-PID guard decisions.
- Route selected pure `lifecycle_process` decisions through the controller while preserving the existing public `TdxTradeManager.pingan.lifecycle_process(...)` result contract.
- Register the new controller-boundary evidence in `FUNCTION_TREE.md` without promoting D-07/D-08 or claiming production trading readiness.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-desktop-trading-management`: adds a controller-boundary requirement for PingAn process lifecycle owner and recorded-PID guard decisions.
- `tdx-function-tree-registry`: registers the process lifecycle controller boundary as bounded architecture evidence.

## Impact

- Affected code: `tdxquant/trade/pingan_lifecycle.py`, `tdxquant/trade/manager.py`.
- Affected tests: `tests/test_trade_manager.py`.
- Affected docs/registry: `FUNCTION_TREE.md`, OpenSpec delta specs.
- No external dependencies, broker behavior, order execution behavior, CLI command shape, or real process start/stop semantics are changed.
