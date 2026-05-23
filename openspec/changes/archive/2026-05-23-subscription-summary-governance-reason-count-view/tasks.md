## 1. Contract

- [x] 1.1 Add OpenSpec proposal, design, and subscription summary delta for governance reason count projection.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Tests

- [x] 2.1 Add bridge HTTP summary-view coverage for `governance.reason_count` while omitting full `governance.reasons` and `governance.actions`.
- [x] 2.2 Add CLI bridge watch-status summary-view coverage for `governance.reason_count` while omitting full `governance.reasons` and `governance.actions`.

## 3. Implementation

- [x] 3.1 Derive `governance.reason_count` in HTTP watch-status summary view.
- [x] 3.2 Derive `governance.reason_count` in CLI watch-status summary view.

## 4. Registry and Verification

- [x] 4.1 Update `FUNCTION_TREE.md` B-16 and E-09 evidence and boundary text.
- [x] 4.2 Run focused tests, OpenSpec validation, function-tree validation, and whitespace checks.
- [x] 4.3 Archive the OpenSpec change and re-run verification before committing.
