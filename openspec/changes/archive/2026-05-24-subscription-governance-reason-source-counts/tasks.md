## 1. Tests

- [x] 1.1 Add observe-state coverage for empty `governance.reason_source_counts`.
- [x] 1.2 Add manual-review coverage for populated `governance.reason_source_counts`.
- [x] 1.3 Add CLI and HTTP summary-view coverage for projected `reason_source_counts`.

## 2. Implementation

- [x] 2.1 Add deterministic reason-source aggregation to subscription governance summary construction.
- [x] 2.2 Project `reason_source_counts` through compact CLI and HTTP summary views while still omitting full reasons.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary without claiming automated governance.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.
