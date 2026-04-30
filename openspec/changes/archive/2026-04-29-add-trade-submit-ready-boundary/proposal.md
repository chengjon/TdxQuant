## Why

稳定桌面交易线已经具备 `trade health`、`trade preflight`、`trade dialog-readiness` 和会自动推进确认的买入工作流，但还缺少一个清晰的“停在确认框前”稳定边界。当前如果调用方想把“提交到确认框可见”和“真正确认委托”分开，只能退回低层 probe 命令，缺少稳定 manager/CLI 入口。

## What Changes

- Add a stable side-effecting-but-pre-confirm workflow at `TdxTradeManager.pingan.submit_ready(...)`.
- Add nested CLI entry `trade submit-ready`.
- Reuse the existing HID submit probe path to fill the form, send the submit keystroke, and stop after confirming the current confirm dialog is visible.
- Attach normalized trade metadata and trade safety metadata for this boundary workflow, with an explicit pre-confirm side-effect classification.
- Keep the workflow non-confirming: it MUST NOT click the confirm dialog and MUST NOT write live-trade artifacts such as last-order state or submission-ledger rows.

## Capabilities

### New Capabilities
- `tdx-desktop-trading-submit-ready`: Stable desktop trading exposes a pre-confirm workflow that stops at the current confirm dialog boundary without advancing the order.

### Modified Capabilities
- `tdx-desktop-trading-cli-entry`: The nested `trade` CLI gains a stable `submit-ready` subcommand.

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
