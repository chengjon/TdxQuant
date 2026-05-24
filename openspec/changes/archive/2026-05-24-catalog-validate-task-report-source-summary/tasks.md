## 1. Tests

- [x] 1.1 Add focused CLI tests for detailed catalog validation exposing `task_report_bundle_step_source_counts`.
- [x] 1.2 Add focused CLI tests for validate summary view copying `task_report_bundle_step_source_counts` without detailed rows.

## 2. Implementation

- [x] 2.1 Aggregate sorted task/report bundle step source counts in `_validate_catalog_registry()`.
- [x] 2.2 Copy the aggregate into validate summary payloads in `_build_catalog_summary_view()`.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` E-11 evidence and boundary without claiming execution readiness.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.
