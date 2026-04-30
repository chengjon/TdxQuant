## Why

`trade_audit` 现在已经支持 `statuses` 的 OR 过滤，也已经补齐了 `buy / buy_submit_once / confirm_current` 三条稳定方法的异常入口，但还不能把它们按“方法集合”聚合成更高一层的诊断视角。现在补 `methods` OR 过滤，可以把“submit path”之类的组合诊断入口稳定下来。

## What Changes

- Add stable multi-method OR filtering to trade-audit daily and period workflows.
- Add CLI support for repeated `--method-any` on task/report trade-audit entrypoints.
- Add stable submit-path exception presets using `methods=[buy_submit_once, confirm_current]` and `statuses=[rejected, failed]`.
- Add catalog entries and at least one diagnostics bundle built on those submit-path presets.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-task-management`: Add multi-method OR filtering for stable trade-audit daily and period workflows.
- `tdx-report-cli-entry`: Add repeated `--method-any` support and stable submit-path exception presets.
- `tdx-command-catalog`: Add submit-path exception entries and diagnostics/follow-up bundles backed by the new multi-method report presets.

## Impact

- Code:
  - `tdxquant/api/task.py`
  - `tdxquant/cli.py`
- Runtime registry:
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
