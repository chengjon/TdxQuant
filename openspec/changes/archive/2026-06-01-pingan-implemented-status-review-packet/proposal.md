## Why

D-07/D-08 promotion readiness can now produce `eligible_for_review`, but that state is still just a machine decision. The next mainline step is to turn that output into a controlled human review input that explains why FUNCTION_TREE was not changed automatically and what evidence still requires manual confirmation.

## What Changes

- Add an `implemented_status_review_packet` to `pingan_promotion_readiness_rollup`.
- Include target nodes, current expected status, decision summary, completed/incomplete gates, evidence validation summaries, and manual confirmation items.
- Keep the packet read-only: it must not execute PingAn workflows, submit orders, or modify `FUNCTION_TREE.md`.
- Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary while preserving `[部分实现]`.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-task-management`: promotion readiness rollup must emit a controlled implemented-status review packet.
- `tdx-function-tree-registry`: D-07/D-08 must register review packet evidence as partial status-review evidence only.

## Impact

- Affected code: `tdxquant/api/task.py`.
- Affected tests: `tests/test_api_manager.py`, `tests/test_function_tree_registry.py`.
- Affected specs: `tdx-task-management`, `tdx-function-tree-registry`.
- No broker, desktop, trade, report, catalog, bundle, or FUNCTION_TREE mutation behavior changes.
