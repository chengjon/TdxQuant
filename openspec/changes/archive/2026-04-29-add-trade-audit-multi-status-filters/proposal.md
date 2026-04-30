## Why

`trade_audit` 当前已经有比较完整的单状态 preset 矩阵，但更高频的“异常复盘”仍然需要调用方手工做多次查询，无法一次表达例如 `rejected + failed` 这样的组合过滤。

## What Changes

- 为稳定 `trade_audit` daily / period workflow 新增多状态 OR 过滤能力
- 为 `report` / `task` 直连入口新增多状态 CLI 参数
- 新增异常类 report presets：
  - `audit-daily-exceptions`
  - `audit-period-exceptions`
- 新增对应 catalog entries 与一个最小异常诊断 bundle

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-task-management`: extend stable trade-audit daily and period workflows to accept multi-status OR filtering
- `tdx-report-cli-entry`: extend stable trade-audit report and task CLI entrypoints to express multi-status filtering
- `tdx-command-catalog`: extend stable audit preset and bundle coverage to expose exception-oriented review entrypoints

## Impact

- code:
  - `tdxquant/api/task.py`
  - `tdxquant/cli.py`
  - `tests/test_api_manager.py`
  - `tests/test_api_cli.py`
- runtime registry:
  - `runtime/report-presets.json`
  - `runtime/command-catalog.json`
  - `runtime/command-bundles.json`
- docs:
  - `docs/TdxQuant_Trade_Audit_Report_Contract.md`
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`
  - `runtime/TdxQuant_Command_Catalog_Usage.md`
