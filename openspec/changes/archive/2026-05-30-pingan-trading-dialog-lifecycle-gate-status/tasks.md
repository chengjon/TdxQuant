## 1. Contract

- [x] 1.1 Add OpenSpec proposal, design, and delta specs for PingAn dialog lifecycle gate status.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add focused failing tests for `desktop_lifecycle_gate_status` on `TdxTradeManager.pingan.dialog_readiness`.
- [x] 2.2 Confirm the focused tests fail because the lifecycle gate status is missing.

## 3. Implementation

- [x] 3.1 Add normalized desktop lifecycle gate status to dialog readiness output.
- [x] 3.2 Keep the dialog readiness path readonly and non-writing.
- [x] 3.3 Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary without changing status.

## 4. Verification

- [x] 4.1 Run focused pytest for trade manager and function tree registry.
- [x] 4.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 4.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
