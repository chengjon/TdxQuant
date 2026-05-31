## Why

D-07/D-08 promotion currently has automated audit outcome coverage and lifecycle evidence, but live/manual acceptance remains explicitly `not_provided`. The next promotion-gate slice should let operators attach verifiable manual acceptance evidence to the existing read-only audit reports without executing trades or implying production readiness.

## What Changes

- Add an optional PingAn live/manual acceptance evidence manifest input to trade audit daily and period reports.
- Validate manifest schema, required outcome coverage, and invalid entries in read-only report output.
- Surface manual evidence inside `acceptance_outcome_coverage_status` with explicit `live_manual_acceptance_complete` and `acceptance_complete` semantics.
- Add CLI plumbing for the existing `task trade-audit-daily-report` and `task trade-audit-period-report` commands.
- Register the evidence and boundary in `FUNCTION_TREE.md` D-07/D-08 without promoting either node.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-task-trade-audit-daily-report`: daily report can attach optional live/manual acceptance manifest evidence.
- `tdx-task-trade-audit-period-report`: period report can attach optional live/manual acceptance manifest evidence.
- `tdx-desktop-trading-safety`: promotion evidence distinguishes automated coverage from operator-provided manual/live acceptance.
- `tdx-function-tree-registry`: D-07/D-08 registry records the new evidence while preserving `[部分实现]`.

## Impact

- Code: `tdxquant/api/task.py`, `tdxquant/cli.py`
- Tests: `tests/test_api_manager.py`, `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`
- Runtime evidence: optional JSON manifest under caller control; no new external dependency.
- Documentation/registry: `FUNCTION_TREE.md` and archived OpenSpec specs.
