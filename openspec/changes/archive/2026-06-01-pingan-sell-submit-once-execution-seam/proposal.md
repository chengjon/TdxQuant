## Why

The first PingAn execution seam slice routed `buy_submit_once` through `tdxquant.trade.pingan_execution`, but `sell_submit_once` still keeps the same gate/dispatch/finalize flow inside `tdxquant/trade/manager.py`. Aligning sell submit-once with the same internal seam closes the D-08 buy/sell asymmetry without changing public behavior.

## What Changes

- Route `TdxTradeManager.pingan.sell_submit_once(...)` through `PingAnExecutionRequest` and `execute_pingan_order(...)`.
- Preserve the existing sell submit-once desktop primitive boundary: it continues to dispatch through `run_pingan_sell_fast`, not a new `run_pingan_sell_submit_once`.
- Add compatibility tests proving the manager delegates through the seam and keeps method identity/gate behavior.
- Update `FUNCTION_TREE.md` evidence for D-08 as an incremental architecture hardening note.

## Capabilities

### New Capabilities

### Modified Capabilities
- `tdx-desktop-trading-management`: Align PingAn buy/sell submit-once manager paths behind the internal PingAn execution seam while preserving public contracts.

## Impact

- Affected code: `tdxquant/trade/manager.py`.
- Affected tests: `tests/test_trade_manager.py` and existing `tests/test_pingan_trade_execution.py`.
- Affected registry/specs: `FUNCTION_TREE.md`, `openspec/specs/tdx-desktop-trading-management/spec.md` after archive.
- No new CLI/task/catalog entry, no new desktop primitive, and no change to live trading safety defaults.
