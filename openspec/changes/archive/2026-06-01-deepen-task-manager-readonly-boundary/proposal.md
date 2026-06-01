## Why

`TdxTaskManager` now holds read-only report/watchlist workflows and higher-risk desktop trade workflows in one large facade class. A read-only task boundary will improve locality for report and discovery tasks without changing task CLI behavior or touching real trading execution paths.

## What Changes

- Add a dedicated read-only task boundary for task workflows that only read, aggregate, validate, plan, or export artifacts.
- Route selected `TdxTaskManager` read-only methods through that boundary while preserving their public method signatures and result payloads.
- Keep desktop trade write paths, broker lifecycle control, and provider mutation workflows out of scope for this change.
- Add public behavior tests for the new boundary and facade delegation.
- Update `FUNCTION_TREE.md` evidence after implementation.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-task-management`: the task management layer gains an explicit read-only task boundary while preserving existing task manager and CLI behavior.

## Impact

- Affected code: `tdxquant/api/task.py`, a new read-only task boundary module under `tdxquant/api/`.
- Affected tests: focused task manager tests in `tests/test_api_manager.py` or a narrower task test file.
- Affected docs/evidence: `FUNCTION_TREE.md`, archived OpenSpec change, and `tdx-task-management` spec.
- No task preset schema change.
- No desktop trade execution, broker lifecycle, provider mutation, or catalog execution semantic change.
