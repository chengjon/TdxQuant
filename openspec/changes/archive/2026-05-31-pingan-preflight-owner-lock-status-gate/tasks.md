## 1. Contract

- [x] 1.1 Create OpenSpec proposal, design, and delta specs for PingAn preflight owner lock status.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add failing manager tests for `promotion_gate_status.lifecycle_owner_lock_status`.
- [x] 2.2 Add failing CLI parser/dispatch tests for `trade preflight` lifecycle owner lock status arguments.

## 3. Implementation

- [x] 3.1 Add optional lifecycle owner lock status inputs to `TdxTradeManager.pingan.preflight(...)`.
- [x] 3.2 Add optional `trade preflight` CLI arguments and forward them to the manager.
- [x] 3.3 Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary without changing status.

## 4. Verification

- [x] 4.1 Run focused pytest for trade manager, API CLI, and FUNCTION_TREE registry.
- [x] 4.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 4.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
