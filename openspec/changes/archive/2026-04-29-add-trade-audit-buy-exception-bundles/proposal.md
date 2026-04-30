## Why

`trade_audit` 已经支持 `method + statuses` 的多维过滤，`buy` 也已经是稳定的基础交易路径，但日常入口还没有把 “基础买入里的 rejected|failed 异常” 做成稳定 preset 和 follow-up bundle。现在补这组入口，可以让 `buy / buy_submit_once / confirm_current` 三条稳定方法的异常排障入口形成对称矩阵。

## What Changes

- Add stable report presets for buy-oriented trade-audit exception review on daily and period workflows.
- Add stable catalog entries mapped to those buy exception presets.
- Add at least one diagnostics bundle and one guarded-buy follow-up bundle that reuse the new presets together with existing entries.
- Update trade-audit contract and roadmap docs to describe the new `buy` exception review entrypoints.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-report-cli-entry`: Add stable buy exception report presets that fix `method=buy` and `statuses=[rejected, failed]`.
- `tdx-command-catalog`: Add stable catalog entries and bundles for buy exception diagnostics and guarded-buy follow-up review.

## Impact

- Runtime registry files:
  - `runtime/report-presets.json`
  - `runtime/command-catalog.json`
  - `runtime/command-bundles.json`
- Tests:
  - `tests/test_api_manager.py`
  - `tests/test_api_cli.py`
- Docs:
  - `docs/TdxQuant_Trade_Audit_Report_Contract.md`
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`
  - `runtime/TdxQuant_Command_Catalog_Usage.md`
