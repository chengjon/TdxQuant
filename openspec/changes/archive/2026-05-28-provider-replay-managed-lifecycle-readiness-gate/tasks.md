# provider replay managed lifecycle readiness gate tasks

## 1. Specification

- [x] Add OpenSpec proposal/design/spec/tasks for managed lifecycle readiness.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add/update CLI readiness tests for managed lifecycle prerequisites and all-requirements-ready state.
- [x] Run focused tests and confirm failure is stale readiness requirement counting.

## 3. Implementation

- [x] Update lifecycle readiness counting to consume managed lifecycle status metadata.
- [x] Keep readiness non-executing and ownership-gated.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming runtime provider or write readiness.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
