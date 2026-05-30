## Why

D-07/D-08 now expose provider/safety, dialog lifecycle, and per-result audit gate status, but maintainers still lack a stable read-only view that separates automated outcome coverage from the remaining live/manual acceptance gap. Without that separation, audit report evidence can be mistaken for production acceptance.

## What Changes

- Add a read-only `acceptance_outcome_coverage_status` payload to PingAn trade audit daily and period reports.
- Summarize covered audit outcome statuses and counts from existing immutable audit artifacts.
- List missing automated outcome statuses separately from live/manual acceptance evidence.
- Register the coverage payload as partial promotion evidence for D-07/D-08 without changing either node from `[部分实现]`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-task-trade-audit-daily-report`: require daily audit reports to expose read-only acceptance/outcome coverage status.
- `tdx-task-trade-audit-period-report`: require period audit reports to expose read-only acceptance/outcome coverage status.
- `tdx-desktop-trading-safety`: register acceptance/outcome coverage status as partial promotion evidence only.
- `tdx-function-tree-registry`: require D-07/D-08 to record the evidence without claiming implemented status.

## Impact

- `tdxquant/api/task.py`
- `tests/test_api_manager.py`
- `FUNCTION_TREE.md`
- OpenSpec specs for trade audit reports, desktop trading safety, and FUNCTION_TREE registry

