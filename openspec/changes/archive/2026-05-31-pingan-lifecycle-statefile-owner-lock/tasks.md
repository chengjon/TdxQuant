## 1. Contract

- [x] 1.1 Add OpenSpec proposal, design, and delta specs for PingAn lifecycle owner lock statefile behavior.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add focused failing tests for acquire/release/status owner lock behavior.
- [x] 2.2 Confirm the focused tests fail because the manager surface is missing.

## 3. Implementation

- [x] 3.1 Add the explicit PingAn lifecycle owner lock manager method.
- [x] 3.2 Persist only the local lifecycle statefile/lock artifacts and keep all process/trade side-effect flags false.
- [x] 3.3 Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary without changing status.

## 4. Verification

- [x] 4.1 Run focused pytest for trade manager and FUNCTION_TREE registry.
- [x] 4.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 4.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
