## 1. Tests

- [x] 1.1 Add CLI summary coverage for `summary_view.capabilities.endpoint_family_counts`.
- [x] 1.2 Assert the summary still omits the full endpoint list.

## 2. Implementation

- [x] 2.1 Add deterministic endpoint family count aggregation for provider replay status summaries.
- [x] 2.2 Include the aggregate in `summary_view.capabilities` without changing probe or lifecycle behavior.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming daemon lifecycle management.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.
