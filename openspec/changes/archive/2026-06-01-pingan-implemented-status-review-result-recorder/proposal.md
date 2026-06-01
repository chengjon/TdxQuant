## Why

D-07/D-08 can now produce an implemented-status review packet, but the maintainer's review decision still has no controlled artifact. The next mainline step is to record approve/reject/defer decisions as evidence without automatically changing `FUNCTION_TREE.md` or executing PingAn workflows.

## What Changes

- Add a PingAn implemented-status review result recorder to task management.
- Accept an existing `implemented_status_review_packet` or a rollup artifact containing that packet as input.
- Record reviewer, outcome, reason, reviewed timestamp, source packet summary, provenance, and explicit non-transition flags in a JSON artifact.
- Reject `approve` when the source packet is not `ready_for_manual_review` and `implemented_status_eligible=true`.
- Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary while preserving `[部分实现]`.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-task-management`: add a controlled PingAn implemented-status review result recorder.
- `tdx-function-tree-registry`: D-07/D-08 must register the review result recorder as partial manual review evidence only.

## Impact

- Affected code: `tdxquant/api/task.py`, `tdxquant/cli.py`.
- Affected tests: `tests/test_api_manager.py`, `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`.
- Affected specs: `tdx-task-management`, `tdx-function-tree-registry`.
- No broker, desktop, trade, report, catalog, bundle, or automatic FUNCTION_TREE mutation behavior changes.
