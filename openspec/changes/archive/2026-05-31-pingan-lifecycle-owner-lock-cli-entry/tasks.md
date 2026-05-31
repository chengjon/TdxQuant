## 1. Contract

- [x] 1.1 Add OpenSpec proposal, design, and delta specs for the PingAn lifecycle owner lock CLI entry.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add focused failing parser and dispatch tests for `trade lifecycle-owner-lock`.
- [x] 2.2 Confirm the focused tests fail because the CLI entry is missing.

## 3. Implementation

- [x] 3.1 Add parser arguments for `trade lifecycle-owner-lock`.
- [x] 3.2 Dispatch the CLI entry to `TdxTradeManager.pingan.lifecycle_owner_lock(...)` without adding process or order execution.
- [x] 3.3 Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary without changing status.

## 4. Verification

- [x] 4.1 Run focused pytest for API CLI and FUNCTION_TREE registry.
- [x] 4.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 4.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
