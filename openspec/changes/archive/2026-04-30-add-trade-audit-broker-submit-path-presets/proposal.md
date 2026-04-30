## Why

`trade_audit` 现在已经支持 `broker`、`methods` 和 `statuses` 三个维度的稳定过滤，但日常入口还停留在“跨 broker 的 submit path 异常视角”。继续补第一组 broker-scoped 组合入口，可以把现有三维过滤正式产品化，方便未来多券商扩展时保持稳定命名和固定调用方式。

## What Changes

- Add stable broker-scoped submit-path exception report presets for `broker=pingan`, `methods=[buy_submit_once, confirm_current]`, and `statuses=[rejected, failed]`.
- Add stable command-catalog entries mapped to those broker-scoped presets.
- Add at least one diagnostics bundle and one confirm follow-up bundle built on the new broker-scoped submit-path entries.
- Update trade-audit report and catalog docs to reflect the new broker/method/status combination entrypoints.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-report-cli-entry`: Add broker-scoped submit-path exception presets for stable trade-audit report workflows.
- `tdx-command-catalog`: Add broker-scoped submit-path exception entries and bundles backed by the new presets.

## Impact

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
