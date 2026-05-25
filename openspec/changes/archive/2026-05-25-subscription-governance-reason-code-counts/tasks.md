## 1. Tests

- [x] 1.1 Add observe-state coverage for empty `governance.reason_summary.reason_code_counts`.
- [x] 1.2 Add manual-review coverage for populated `governance.reason_summary.reason_code_counts`.
- [x] 1.3 Add bridge HTTP and CLI summary projection coverage for the new reason-code counts.

## 2. Implementation

- [x] 2.1 Add deterministic reason-code count aggregation to `_build_subscription_watch_governance_reason_summary()`.
- [x] 2.2 Preserve existing governance fields, advisory decisions, actions, and summary-view omission of raw reason/action lists.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary without claiming automated governance.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator.
