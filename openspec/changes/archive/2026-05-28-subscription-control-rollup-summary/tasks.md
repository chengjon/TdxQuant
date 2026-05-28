# Tasks

## 1. Specification

- [x] Add proposal, design, spec delta, and tasks for control rollup summary.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] Add failing core status-summary assertions for `status_summary.control_rollup`.
- [x] Add failing HTTP summary-view assertions for `status_summary.control_rollup`.
- [x] Add failing CLI summary-view assertions for `status_summary.control_rollup`.
- [x] Confirm focused tests fail because the rollup is missing or not projected.

## 3. Implementation

- [x] Add core control rollup derivation from existing reconciled control payload.
- [x] Project control rollup through HTTP summary view.
- [x] Project control rollup through CLI summary view.
- [x] Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] Run focused tests.
- [x] Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
