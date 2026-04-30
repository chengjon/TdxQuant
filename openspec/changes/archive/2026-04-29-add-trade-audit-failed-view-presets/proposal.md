## Why

`trade_audit` 的 status-oriented preset 矩阵现在已经覆盖了 `confirmed`、`replayed` 和 `rejected` 的常用视角，但 `failed` 仍然缺少稳定入口。调用方如果要专门复盘失败审计，仍然需要重复显式传 `status=failed`。

## What Changes

- 为 `trade_audit` 新增稳定 report presets：
  - `audit-daily-failed`
  - `audit-period-failed`
- 为这些 presets 新增稳定 command catalog entries：
  - `audit-daily-failed`
  - `audit-period-failed`
- 新增一个最小失败诊断 bundle：
  - `audit-failure-diagnostics`

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-report-cli-entry`: extend stable trade-audit report preset coverage to include failed-oriented daily and period views
- `tdx-command-catalog`: extend stable catalog entry and bundle coverage for failed-oriented trade-audit diagnostics

## Impact

- runtime registry:
  - `runtime/report-presets.json`
  - `runtime/command-catalog.json`
  - `runtime/command-bundles.json`
- docs:
  - `docs/TdxQuant_Trade_Audit_Report_Contract.md`
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`
  - `runtime/TdxQuant_Command_Catalog_Usage.md`
