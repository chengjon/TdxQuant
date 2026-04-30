## Why

`trade_audit` 现在已经有稳定的 lookup、daily 和 period report workflow，但它们还没有真正进入日常入口层。调用方仍然需要显式记住：

- `report audit-daily`
- `report audit-period`
- 对应的常用默认参数

这与现有 `daily-review / recent-ledger / period-review` 的体验不一致，也让 `catalog` 不能把 `trade_audit` 作为完整的稳定日常入口暴露出来。

## What Changes

- 为 `trade_audit` 新增稳定 report presets：
  - `audit-daily-review`
  - `audit-daily-confirmed`
  - `audit-period-review`
- 为 `trade_audit` 新增稳定 command catalog entries：
  - `audit-daily-review`
  - `audit-daily-confirmed`
  - `audit-period-review`
- 新增一个最小诊断 bundle，组合既有台账入口和新的 audit report 入口

## Impact

- 更新 specs：
  - `tdx-report-cli-entry`
  - `tdx-command-catalog`
- 影响集中在 runtime 配置与文档：
  - `runtime/report-presets.json`
  - `runtime/command-catalog.json`
  - `runtime/command-bundles.json`
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`
