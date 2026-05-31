## 1. Contract

- [x] 1.1 Create OpenSpec proposal, design, and delta specs for task-run owner-lock guard overrides.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add failing `task run` parser/dispatch tests for lifecycle owner-lock guard CLI overrides.
- [x] 2.2 Add failing preset-option preservation tests for lifecycle owner-lock guard values.

## 3. Implementation

- [x] 3.1 Add lifecycle owner-lock guard arguments to `task run`.
- [x] 3.2 Preserve preset-provided stale timeout and use a stable default only when missing.
- [x] 3.3 Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary without changing status.

## 4. Verification

- [x] 4.1 Run focused pytest for API CLI and FUNCTION_TREE registry.
- [x] 4.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 4.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
