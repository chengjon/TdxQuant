## Why

`trade_audit` 已经支持 `method + statuses` 的多维过滤，`buy_submit_once` 也已经是稳定的完整提交流程，但日常入口还没有把 “完整提交流程里的 rejected|failed 异常” 做成稳定 preset 和 follow-up bundle。现在补这组入口，可以让 `submit-once` 交易线的排障路径和 `confirm_current` 保持对称。

## What Changes

- Add stable report presets for submit-once-oriented trade-audit exception review on daily and period workflows.
- Add stable catalog entries mapped to those submit-once exception presets.
- Add at least one diagnostics bundle and one submit-once follow-up bundle that reuse the new presets together with existing entries.
- Update trade-audit contract and roadmap docs to describe the new `buy_submit_once` exception review entrypoints.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-report-cli-entry`: Add stable submit-once exception report presets that fix `method=buy_submit_once` and `statuses=[rejected, failed]`.
- `tdx-command-catalog`: Add stable catalog entries and bundles for submit-once exception diagnostics and submit-once follow-up review.

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
