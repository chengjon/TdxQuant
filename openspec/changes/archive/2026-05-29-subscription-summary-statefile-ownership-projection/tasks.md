## 1. Implementation

- [x] Add optional statefile ownership projection support to `build_subscription_watch_status_summary()`.
- [x] Pass the existing controller `statefile_ownership` diagnostic into status summary construction.
- [x] Include `statefile_ownership` in bridge watch-status summary-view `status_summary` projection.

## 2. Tests

- [x] Add focused tests for detailed status summary statefile ownership projection.
- [x] Add focused tests for bridge watch-status summary view preserving the compact ownership projection.

## 3. Registry and Validation

- [x] Update `FUNCTION_TREE.md` B-16/E-09 evidence/boundary with this read-only summary projection.
- [x] Run focused pytest for subscription background and CLI summary coverage.
- [x] Run `openspec validate --all --strict`.
- [x] Run `git diff --check`.
- [x] Run `python scripts/validate_function_tree_registry.py`.
