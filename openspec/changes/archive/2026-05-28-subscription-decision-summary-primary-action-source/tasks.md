# Tasks

## 1. Specification

- [x] Add proposal, design, spec delta, and tasks for decision-summary primary action reason source.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] Add failing HTTP summary-view assertion for `decision_summary.primary_action_reason_source`.
- [x] Add failing CLI summary-view assertion for `decision_summary.primary_action_reason_source`.
- [x] Confirm focused tests fail because the field is missing.

## 3. Implementation

- [x] Add the primary action reason source field to HTTP summary-view decision summary.
- [x] Add the primary action reason source field to CLI summary-view decision summary.
- [x] Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] Run focused tests.
- [x] Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
