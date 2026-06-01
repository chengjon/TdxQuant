## 1. Red Tests

- [x] 1.1 Add parser test for `trade acceptance-evidence --view summary`.
- [x] 1.2 Add handler test asserting summary view contents and no execution side effects.
- [x] 1.3 Run focused tests and confirm they fail before implementation.

## 2. Implementation

- [x] 2.1 Add `--view detailed|summary` to `trade acceptance-evidence`.
- [x] 2.2 Add summary projection helper and attach `data.summary_view` for summary view.
- [x] 2.3 Preserve detailed default behavior.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` D-13 evidence and boundary.
- [x] 3.2 Run focused pytest and full `tests/test_api_cli.py`.
- [x] 3.3 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 3.4 Archive the OpenSpec change.
- [x] 3.5 Re-run verification after archive.
- [x] 3.6 Commit only this slice.
