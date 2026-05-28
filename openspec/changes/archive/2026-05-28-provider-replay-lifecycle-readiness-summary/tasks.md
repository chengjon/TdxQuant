# provider replay lifecycle readiness summary tasks

## 1. Specification

- [x] Add an OpenSpec delta requiring read-only lifecycle readiness summaries.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add parser coverage for `provider-replay lifecycle-readiness`.
- [x] Add detailed readiness assertions for default no-statefile-check behavior.
- [x] Add summary readiness assertions with opt-in valid statefile diagnostics.
- [x] Run focused tests and confirm failure is the missing readiness command/output.

## 3. Implementation

- [x] Add lifecycle-readiness parser support.
- [x] Build a read-only detailed readiness summary from existing lifecycle status and optional statefile diagnostics.
- [x] Add summary-view projection without enabling lifecycle control.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming daemon lifecycle control.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
