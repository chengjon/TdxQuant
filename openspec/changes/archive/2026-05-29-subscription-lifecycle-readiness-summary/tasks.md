## 1. Tests

- [x] 1.1 Add focused background status coverage for blocked `status_summary.lifecycle_readiness`.
- [x] 1.2 Add focused background status coverage for ready `status_summary.lifecycle_readiness`.
- [x] 1.3 Add focused CLI summary-view coverage for `status_summary.lifecycle_readiness`.
- [x] 1.4 Add focused HTTP summary-view coverage for `status_summary.lifecycle_readiness`.

## 2. Implementation

- [x] 2.1 Add a compact lifecycle readiness projection derived from existing status evidence.
- [x] 2.2 Preserve lifecycle readiness through CLI and HTTP summary allow-lists.

## 3. Registry and Validation

- [x] 3.1 Update `FUNCTION_TREE.md` B-16/E-09 evidence/boundary for lifecycle readiness summary.
- [x] 3.2 Run focused pytest for subscription background, HTTP, and CLI coverage.
- [x] 3.3 Run `openspec validate --all --strict`.
- [x] 3.4 Run `git diff --check`.
- [x] 3.5 Run `python scripts/validate_function_tree_registry.py`.
