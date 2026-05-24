## 1. Tests

- [x] 1.1 Add detailed `catalog validate` coverage for `task_report_bundle_label_counts`.
- [x] 1.2 Add `catalog validate --view summary` coverage that projects `task_report_bundle_label_counts`.

## 2. Implementation

- [x] 2.1 Aggregate deterministic label counts for resolved task+report bundles.
- [x] 2.2 Copy `task_report_bundle_label_counts` into the reduced summary view without exposing full bundles.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` E-11 evidence and boundary without claiming execution or workflow-builder support.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.
