# provider replay process ownership diagnostics tasks

## 1. Specification

- [x] Add an OpenSpec delta requiring read-only process ownership diagnostics.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add provider replay helper tests for owned, non-running, and identity-mismatch diagnostics.
- [x] Add daemon status/readiness tests proving ownership diagnostics are surfaced and readiness counts owned process identity only when proven.
- [x] Run focused tests and confirm failure is missing ownership diagnostics.

## 3. Implementation

- [x] Add process ownership diagnostic helper.
- [x] Wire diagnostics into managed daemon status.
- [x] Wire ownership diagnostic into lifecycle readiness counting.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming real provider lifecycle completion.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
