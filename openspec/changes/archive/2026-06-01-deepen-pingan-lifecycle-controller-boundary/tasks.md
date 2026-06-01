## 1. Red Tests

- [x] 1.1 Add a public boundary test for owner-gate rejection without side effects.
- [x] 1.2 Add a public boundary test for restart/backoff policy decisions without process execution.
- [x] 1.3 Run the new lifecycle controller tests and confirm they fail before implementation.

## 2. Controller Implementation

- [x] 2.1 Introduce a PingAn lifecycle controller module under `tdxquant/trade/`.
- [x] 2.2 Route supervisor owner-gate rejection payload construction through the controller boundary.
- [x] 2.3 Route restart/backoff policy decisions through the controller boundary.
- [x] 2.4 Preserve existing public `TdxTradeManager.pingan.lifecycle_supervisor_tick` behavior and side-effect boundaries.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` evidence and boundary for the PingAn lifecycle controller boundary.
- [x] 3.2 Run focused PingAn lifecycle tests.
- [x] 3.3 Run `openspec validate --all --strict`.
- [x] 3.4 Run `git diff --check`.
- [x] 3.5 Run `python scripts/validate_function_tree_registry.py`.
- [x] 3.6 Archive the OpenSpec change and repeat verification.
