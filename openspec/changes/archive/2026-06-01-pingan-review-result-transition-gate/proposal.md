## Why

D-07/D-08 now have a controlled human review-result artifact, but there is still no fail-closed gate that says whether that artifact is sufficient to start an explicit FUNCTION_TREE status-transition review. The next mainline step is to turn the review result into a deterministic transition checklist without automatically changing status.

## What Changes

- Add a PingAn implemented-status transition gate task.
- Load a `tdx.desktop_trade.pingan_implemented_status_review_result.v1` artifact and validate schema, provenance, outcome, target nodes, packet status, and non-transition flags.
- Return a deterministic `implemented_status_transition_gate` with `eligible_for_status_transition_review`, `gate_status`, `completed_checks`, `blocked_reasons`, and manual transition checklist.
- Expose a CLI task entry for direct operator use.
- Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary while preserving `[部分实现]`.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-task-management`: add a read-only PingAn review-result transition gate.
- `tdx-function-tree-registry`: D-07/D-08 must register the transition gate as partial pre-transition evidence only.

## Impact

- Affected code: `tdxquant/api/task.py`, `tdxquant/cli.py`.
- Affected tests: `tests/test_api_manager.py`, `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`.
- Affected specs: `tdx-task-management`, `tdx-function-tree-registry`.
- No broker, desktop, trade, report, catalog, bundle, or automatic FUNCTION_TREE mutation behavior changes.
