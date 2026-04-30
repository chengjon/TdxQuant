## Why

当前 `trade_audit` 已经有基础的日常入口，但 richer 组合仍然偏少：

- `audit-daily-review`
- `audit-daily-confirmed`
- `audit-period-review`
- `audit-diagnostics`
- `confirm-audit-review`

这意味着两个常见场景还没有被正式收口：

- 面向拒单/异常排障的稳定 `rejected` 审计视角
- `confirm-current` 之后继续串联成交日报与确认审计的固定 follow-up

## What Changes

- 为 `trade_audit` 新增稳定 report presets：
  - `audit-daily-rejected`
  - `audit-period-rejected`
- 为这些 presets 新增稳定 command catalog entries：
  - `audit-daily-rejected`
  - `audit-period-rejected`
- 新增两个最小 bundle：
  - `audit-rejection-diagnostics`
  - `confirm-complete-review`

## Impact

- 更新 specs：
  - `tdx-report-cli-entry`
  - `tdx-command-catalog`
- 影响集中在 runtime 配置与文档：
  - `runtime/report-presets.json`
  - `runtime/command-catalog.json`
  - `runtime/command-bundles.json`
  - `docs/TdxQuant_Trade_Audit_Report_Contract.md`
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`
