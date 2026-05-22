## Why

`FUNCTION_TREE.md` D-11 still marks trade audit daily/period diagnostics as partial because the reports expose counts and filters, but do not summarize requested order value coverage from the audit payloads. The next useful diagnostic is a read-only amount view that uses existing audit data without implying fill quality or PnL support.

## What Changes

- Add a `value_diagnostics` section to trade audit daily and period reports.
- Compute requested order value only when an audit entry has numeric `price` and `quantity` in its result data.
- Report total priced/unpriced coverage and requested order value by status and method.
- Keep all calculations read-only and local to existing audit files.
- Do not infer fills, execution quality, slippage, fees, realized PnL, or broker account balances.
- Update `FUNCTION_TREE.md` D-11 with explicit evidence and boundary.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-task-trade-audit-daily-report`: daily trade audit reports expose requested-value diagnostics from existing audit payloads.
- `tdx-task-trade-audit-period-report`: period trade audit reports expose requested-value diagnostics from existing audit payloads.

## Impact

- Affected code: `tdxquant/api/task.py`.
- Affected tests: `tests/test_api_manager.py`.
- Affected registry/specs: `FUNCTION_TREE.md`, OpenSpec daily and period trade audit report specs.
- No new external dependencies, broker calls, account queries, or mutation paths.
