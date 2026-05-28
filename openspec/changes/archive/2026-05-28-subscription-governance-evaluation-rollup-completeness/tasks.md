# Tasks

## 1. Specification

- [x] Add proposal, design, spec delta, and tasks for the read-only evaluation rollup completeness slice.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] Add failing HTTP summary-view assertions for the new evaluation rollup fields.
- [x] Add failing CLI summary-view assertions for the new evaluation rollup fields.
- [x] Confirm the focused tests fail because the fields are missing.

## 3. Implementation

- [x] Add the read-only fields to HTTP summary-view evaluation rollup.
- [x] Add the read-only fields to CLI summary-view evaluation rollup.
- [x] Update FUNCTION_TREE B-16/E-09 evidence and boundary without changing their `[部分实现]` status.

## 4. Verification

- [x] Run focused tests.
- [x] Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
