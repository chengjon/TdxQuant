## 1. Implementation

- [x] Include `boundary` in CLI watch-status summary `status_summary` projection.
- [x] Include `boundary` in HTTP watch-status summary `status_summary` projection.

## 2. Tests

- [x] Add focused CLI summary-view coverage for `status_summary.boundary`.
- [x] Add focused HTTP summary-view coverage for `status_summary.boundary`.

## 3. Registry and Validation

- [x] Update `FUNCTION_TREE.md` B-16/E-09 evidence/boundary for summary boundary projection.
- [x] Run focused pytest for HTTP/CLI/subscription summary coverage.
- [x] Run `openspec validate --all --strict`.
- [x] Run `git diff --check`.
- [x] Run `python scripts/validate_function_tree_registry.py`.
