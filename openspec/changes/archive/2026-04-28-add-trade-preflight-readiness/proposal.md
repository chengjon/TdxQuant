## Why

桌面交易线已经有稳定 `trade health`，但它只回答 broker/runtime 和可选 HID 路径是否可用，仍然不能直接回答“这一次具体下单请求现在是否具备稳定执行前提”。当前这部分判断分散在 broker detect、risk gate、submission ledger 和低层 probe 命令里，日常使用边界仍然偏散。

## What Changes

- Add a stable non-side-effecting `preflight` workflow at `TdxTradeManager.pingan.preflight(...)`.
- Add nested CLI entry `trade preflight`.
- Evaluate broker runtime health, buy-page detection, order-request risk gate, submission-key idempotency, and HID ping in one structured summary.
- Keep the workflow read-only: it must not write last-order state, append event rows, or append submission-ledger rows.

## Capabilities

### New Capabilities
- `tdx-desktop-trading-preflight`: Stable desktop trade management exposes a single-request read-only preflight workflow for Ping An trading readiness.

### Modified Capabilities
- `tdx-desktop-trading-cli-entry`: The nested `trade` CLI gains a stable `preflight` subcommand.

## Impact

- Affected code:
  - `tdxquant/trade/manager.py`
  - `tdxquant/trade/context.py`
  - `tdxquant/cli.py`
  - `tests/test_trade_manager.py`
  - `tests/test_api_cli.py`
- Affected docs:
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`
