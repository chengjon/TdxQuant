## 1. Contract

- [x] 1.1 Create OpenSpec proposal, design, and delta specs for the execution owner-lock guard.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add failing manager tests for execution guard rejection and pass-through behavior.
- [x] 2.2 Add failing gateway/CLI tests for forwarding guard arguments.

## 3. Implementation

- [x] 3.1 Add owner-lock guard evaluation to PingAn buy/sell/submit-once manager methods.
- [x] 3.2 Thread guard options through `PingAnDesktopTraderGateway`.
- [x] 3.3 Add stable trade CLI guard arguments and forwarding.
- [x] 3.4 Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary without changing status.

## 4. Verification

- [x] 4.1 Run focused pytest for trade manager, PingAn gateway, API CLI, and FUNCTION_TREE registry.
- [x] 4.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 4.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
