# Tasks: Subscription Summary Schema Version View

## 1. Tests

- [x] 1.1 Add CLI summary-view coverage for `status_summary.schema_version`.
- [x] 1.2 Add HTTP summary-view coverage for `status_summary.schema_version`.

## 2. Implementation

- [x] 2.1 Copy `status_summary.schema_version` into `_build_bridge_watch_status_summary_payload()` when present.
- [x] 2.2 Preserve the existing compact summary omissions for raw status and full governance lists.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` E-09 evidence and boundary without claiming lifecycle or governance automation.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.
