## 1. Implementation

- [x] Include `statefile_ownership` in HTTP watch-status summary `status_summary` projection.
- [x] Include `supervisor_daemon` in HTTP watch-status summary `status_summary` projection while preserving existing top-level projection.

## 2. Tests

- [x] Add focused HTTP summary-view coverage for `status_summary.statefile_ownership`.
- [x] Add focused HTTP summary-view coverage for `status_summary.supervisor_daemon`.

## 3. Registry and Validation

- [x] Update `FUNCTION_TREE.md` B-16/E-09 evidence/boundary for HTTP summary parity.
- [x] Run focused pytest for HTTP/CLI/subscription summary coverage.
- [x] Run `openspec validate --all --strict`.
- [x] Run `git diff --check`.
- [x] Run `python scripts/validate_function_tree_registry.py`.
