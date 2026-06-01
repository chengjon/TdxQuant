## Why

D-07/D-08 now have a read-only transition gate, but there is still no controlled writer that can perform an explicit FUNCTION_TREE status transition when a maintainer provides an eligible gate and confirms the transition. The next mainline step is to implement that writer with strong fail-closed behavior and an audit record.

## What Changes

- Add a PingAn implemented-status transition writer task.
- Read an eligible `implemented_status_transition_gate` artifact.
- Validate target nodes, current FUNCTION_TREE status, non-transition flags, gate eligibility, and explicit operator confirmation.
- In dry-run mode, return the exact nodes and status changes that would be applied without writing files.
- In apply mode, update a caller-provided `FUNCTION_TREE.md` path from `[部分实现]` to `[已实现]` for D-07/D-08 and write a transition record artifact.
- Expose a CLI task entry for direct operator use.
- Update repository `FUNCTION_TREE.md` to register the writer capability while keeping D-07/D-08 partial until a real transition is executed against the registry.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-task-management`: add a guarded PingAn implemented-status transition writer and record.
- `tdx-function-tree-registry`: D-07/D-08 must register the transition writer as available transition machinery without implying the transition has run.

## Impact

- Affected code: `tdxquant/api/task.py`, `tdxquant/cli.py`.
- Affected tests: `tests/test_api_manager.py`, `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`.
- Affected specs: `tdx-task-management`, `tdx-function-tree-registry`.
- No broker, desktop, trade, report, catalog, bundle, order, or PingAn workflow execution behavior changes.
