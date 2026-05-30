## 1. Contract

- [x] 1.1 Add OpenSpec proposal, design, and delta specs for passive PingAn exception popup readiness.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add a focused failing test for `dialog_readiness` exception popup lookup evidence.
- [x] 2.2 Confirm the focused test fails because `exception_popup_lookup` is missing.

## 3. Implementation

- [x] 3.1 Add passive exception popup classification to PingAn dialog readiness result checks.
- [x] 3.2 Include exception popup lookup in `desktop_lifecycle_gate_status` while preserving non-side-effecting behavior.
- [x] 3.3 Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary without changing status.

## 4. Verification

- [x] 4.1 Run focused pytest for dialog readiness and FUNCTION_TREE registry.
- [x] 4.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 4.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
