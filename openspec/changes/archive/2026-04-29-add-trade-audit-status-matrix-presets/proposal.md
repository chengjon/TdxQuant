## Why

`trade_audit` 的基础 review / confirmed / rejected 入口已经稳定，但 status 维度的 preset 矩阵仍然不完整。当前缺的主要是：

- `period confirmed`
- `daily replayed`
- `period replayed`

这会让调用方在做成功复盘或 replay 诊断时，仍然要重复显式传 `status` 参数，和现在已经收口好的 `confirmed` / `rejected` 体验不一致。

## What Changes

- 为 `trade_audit` 新增稳定 report presets：
  - `audit-period-confirmed`
  - `audit-daily-replayed`
  - `audit-period-replayed`
- 为这些 presets 新增稳定 command catalog entries：
  - `audit-period-confirmed`
  - `audit-daily-replayed`
  - `audit-period-replayed`
- 新增两条最小 review bundle：
  - `audit-confirmed-review`
  - `audit-replay-review`

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-report-cli-entry`: extend stable report preset coverage for additional `trade_audit` status-oriented presets
- `tdx-command-catalog`: extend stable catalog entry and bundle coverage for richer `trade_audit` review combinations

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
