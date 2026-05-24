# Tasks: Catalog Validate Task Report Step Count

## 1. Tests

- [x] 1.1 Add failing detailed catalog validation coverage for `task_report_bundle_step_count`.
- [x] 1.2 Add failing summary view coverage for `task_report_bundle_step_count`.
- [x] 1.3 Add failing no-match coverage with zero task/report bundle step count.

## 2. Implementation

- [x] 2.1 Derive `task_report_bundle_step_count` during catalog bundle validation.
- [x] 2.2 Copy the scalar into `catalog validate --view summary`.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` E-11 evidence and boundary without claiming execution or workflow-builder support.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.
