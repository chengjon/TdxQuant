# Tasks

## 1. Specification

- [x] Add proposal, design, spec delta, and tasks for decision-summary reason key counts.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] Add failing HTTP summary-view assertions for `decision_summary.reason_source_key_count` and `decision_summary.reason_code_key_count`.
- [x] Add failing CLI summary-view assertions for `decision_summary.reason_source_key_count` and `decision_summary.reason_code_key_count`.
- [x] Confirm focused tests fail because the fields are missing.

## 3. Implementation

- [x] Add the reason key count fields to HTTP summary-view decision summary.
- [x] Add the reason key count fields to CLI summary-view decision summary.
- [x] Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] Run focused tests.
- [x] Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
