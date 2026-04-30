## Why

当前稳定交易主线已经有 `last_order_state`、`order_event_log` 和可选 `submission_ledger`，但还缺少“一次交易结果对应一份不可变审计快照”的治理层。只靠可覆盖 state 文件和连续追加日志，不足以给后续排障、人工复核和上层系统对账提供稳定的单次审计对象。

## What Changes

- Add an immutable desktop trade audit artifact for stable trade workflows that persist finalized results.
- Attach a normalized `trade_audit` summary to stable finalized trade results and preserve the same correlation data in persisted state/event artifacts.
- Expose the configured trade-audit artifact target together with the existing trade artifact target discovery paths.

## Capabilities

### New Capabilities
- `tdx-desktop-trading-audit`: Immutable audit artifact contract and normalized audit summary for finalized stable desktop trade workflows.

### Modified Capabilities
- `tdx-desktop-trading-management`: Persisted stable desktop trade artifacts now include normalized trade-audit correlation and expose the audit artifact target path as part of artifact governance.

## Impact

- Affected code:
  - `tdxquant/trade/context.py`
  - `tdxquant/trade/manager.py`
  - `tests/test_trade_manager.py`
- Affected docs:
  - desktop trade contract / function map / next-step documentation
