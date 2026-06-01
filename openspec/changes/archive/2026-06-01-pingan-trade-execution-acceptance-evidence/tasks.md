## 1. Red Tests

- [x] 1.1 Add a manager test asserting PingAn acceptance evidence summary is read-only and covers D-07/D-08 trade surfaces.
- [x] 1.2 Add CLI parser/dispatch tests for `trade acceptance-evidence`.
- [x] 1.3 Run focused tests and confirm they fail before implementation.

## 2. Implementation

- [x] 2.1 Add `TdxTradeManager.pingan.acceptance_evidence(...)`.
- [x] 2.2 Add `trade acceptance-evidence` parser and handler.
- [x] 2.3 Preserve no-execution behavior and explicit side-effect flags.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` with a bounded D-07/D-08-linked acceptance evidence summary node.
- [x] 3.2 Run focused pytest.
- [x] 3.3 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 3.4 Archive the OpenSpec change.
- [x] 3.5 Re-run verification after archive.
- [x] 3.6 Commit only this slice.
