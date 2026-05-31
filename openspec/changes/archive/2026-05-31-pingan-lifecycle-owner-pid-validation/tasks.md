## 1. Contract

- [x] 1.1 Add OpenSpec proposal, design, and delta specs for PingAn owner PID validation.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add focused failing tests for owner PID validation fields.
- [x] 2.2 Confirm the focused tests fail because PID validation fields are missing.

## 3. Implementation

- [x] 3.1 Add local owner PID validation to PingAn lifecycle owner lock payloads.
- [x] 3.2 Preserve non-control boundaries and keep `pid_ownership_claimed=false`.
- [x] 3.3 Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary without changing status.

## 4. Verification

- [x] 4.1 Run focused pytest for trade manager and FUNCTION_TREE registry.
- [x] 4.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 4.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
