## Why

`trade_audit` 现在已经支持 `method + statuses` 的多维过滤，但日常入口还停留在按状态或总览视角。`confirm_current` 这条 split-step 路径已经稳定，应该补一组可复用的异常 preset 和 follow-up bundle，避免每次手动拼 `--method confirm_current --status-any rejected --status-any failed`。

## What Changes

- Add stable report presets for confirm-oriented trade-audit exception review on daily and period workflows.
- Add stable catalog entries mapped to those confirm-oriented exception presets.
- Add at least one diagnostics bundle and one split-step confirm follow-up bundle that reuse the new presets together with existing entries.
- Update trade-audit contract and roadmap docs to describe the new multidimensional daily入口。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-report-cli-entry`: Add stable confirm-oriented exception report presets that fix `method=confirm_current` and `statuses=[rejected, failed]`.
- `tdx-command-catalog`: Add stable catalog entries and bundles for confirm-oriented exception diagnostics and split-step confirm follow-up review.

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
