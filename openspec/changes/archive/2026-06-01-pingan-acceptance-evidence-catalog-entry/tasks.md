## 1. Red Tests

- [x] 1.1 Add catalog list test for `trade-acceptance-evidence` under acceptance/read-only labels.
- [x] 1.2 Add catalog plan summary test asserting non-executing trade boundary for `acceptance-evidence`.
- [x] 1.3 Run focused tests and confirm they fail before implementation.

## 2. Implementation

- [x] 2.1 Add `acceptance-evidence-default` to `runtime/trade-presets.json`.
- [x] 2.2 Add `trade-acceptance-evidence` to `runtime/command-catalog.json`.
- [x] 2.3 Extend catalog trade plan boundary classification if required.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` D-13 evidence and boundary.
- [x] 3.2 Run focused pytest.
- [x] 3.3 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 3.4 Archive the OpenSpec change.
- [x] 3.5 Re-run verification after archive.
- [x] 3.6 Commit only this slice.
