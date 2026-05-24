## 1. Tests

- [x] 1.1 Add observe-state coverage for empty `governance.action_summary.severity_counts`.
- [x] 1.2 Add manual-review coverage for populated `governance.action_summary.severity_counts`.

## 2. Implementation

- [x] 2.1 Add deterministic severity count aggregation to `_build_subscription_watch_governance_action_summary()`.
- [x] 2.2 Preserve existing action summary fields and summary-view omission of full action lists.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary without claiming automated governance.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.
