# provider replay managed lifecycle status summary tasks

## 1. Specification

- [x] Add proposal/design/spec/tasks for managed lifecycle status summary.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add provider replay status tests for configured managed lifecycle availability while preserving unconfigured unsupported behavior.
- [x] Add CLI summary view tests proving lifecycle status summary reports managed availability without dispatching control.
- [x] Run focused tests and confirm failure is the stale unsupported lifecycle status fields.

## 3. Implementation

- [x] Update lifecycle status metadata for configured lifecycle statefile.
- [x] Update summary view fields if needed while keeping derivation read-only.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming real provider or write readiness.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
