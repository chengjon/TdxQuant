# provider replay lifecycle control plan tasks

## 1. Specification

- [x] Add an OpenSpec delta requiring non-executing lifecycle control plans.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add parser coverage for `provider-replay lifecycle-plan`.
- [x] Add focused dispatch assertions for detailed and summary lifecycle plans.
- [x] Run focused tests and confirm failure is the missing command/plan.

## 3. Implementation

- [x] Add CLI parser support for `provider-replay lifecycle-plan`.
- [x] Build a read-only detailed lifecycle plan from existing lifecycle status.
- [x] Add summary-view projection without executing lifecycle control, serving, or probing.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming daemon lifecycle control.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
