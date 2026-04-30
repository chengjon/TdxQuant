## Why

桌面交易线现在已经有稳定的 `submit-ready` pre-confirm 边界，但还缺少与之对称的第二段 workflow。调用方如果要从“当前确认框已就绪”继续推进到“确认已点击、结果窗已识别/可选关闭”，仍然只能依赖完整买入流程或低层实验命令。

## What Changes

- Add a stable live-side-effecting `TdxTradeManager.pingan.confirm_current(...)` workflow for advancing the currently visible confirm dialog.
- Add nested CLI entry `trade confirm-current`.
- Reuse the stable confirm/result lookup rules to click the current confirm dialog, detect the result dialog, and optionally close the result dialog.
- Persist standard trade state/event artifacts for the confirmed action, while keeping submission-ledger behavior out of this boundary workflow.

## Capabilities

### New Capabilities
- `tdx-desktop-trading-confirm-current`: Stable desktop trading exposes a workflow that advances the currently visible confirm dialog and handles the current result dialog boundary.

### Modified Capabilities
- `tdx-desktop-trading-cli-entry`: The nested `trade` CLI gains a stable `confirm-current` subcommand.

## Impact

- Affected code:
  - `tdxquant/trade/manager.py`
  - `tdxquant/cli.py`
  - `tests/test_trade_manager.py`
  - `tests/test_api_cli.py`
- Affected docs:
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`
