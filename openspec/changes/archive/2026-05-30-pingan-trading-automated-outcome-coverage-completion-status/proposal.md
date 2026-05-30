## Why

`acceptance_outcome_coverage_status` lists missing automated outcome statuses, but it does not expose a stable boolean that separates automated outcome coverage completion from live/manual acceptance completion. D-07/D-08 need that split to avoid treating local audit coverage as full acceptance.

## What Changes

- Add automated coverage completion fields to daily and period trade audit report `acceptance_outcome_coverage_status`.
- Keep `acceptance_complete=false` unless live/manual acceptance is provided by a later change.
- Add focused tests for a report covering confirmed, rejected, failed, and exception outcomes.
- Register the evidence in `FUNCTION_TREE.md` while keeping D-07/D-08 `[部分实现]`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-task-trade-audit-daily-report`: expose automated outcome coverage completion status in the read-only coverage payload.
- `tdx-task-trade-audit-period-report`: expose automated outcome coverage completion status in the read-only coverage payload.
- `tdx-desktop-trading-safety`: register automated coverage completion as partial promotion evidence only.
- `tdx-function-tree-registry`: require D-07/D-08 to record automated coverage completion without claiming implemented status.

## Impact

- `tdxquant/api/task.py`
- `tests/test_api_manager.py`
- `FUNCTION_TREE.md`
- OpenSpec specs for trade audit reports, desktop trading safety, and FUNCTION_TREE registry

