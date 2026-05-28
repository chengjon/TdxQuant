# provider replay lifecycle plan statefile diagnostics tasks

## 1. Specification

- [x] Add an OpenSpec delta requiring opt-in statefile diagnostics in lifecycle plans.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add parser coverage for `provider-replay lifecycle-plan --include-statefile-check`.
- [x] Add detailed plan assertions for embedded statefile diagnostics.
- [x] Add summary-view assertions for compact statefile diagnostics.
- [x] Run focused tests and confirm failure is the missing plan diagnostics.

## 3. Implementation

- [x] Add lifecycle-plan parser flags for statefile diagnostics.
- [x] Embed compact statefile diagnostics in detailed lifecycle plans only when explicitly requested.
- [x] Project diagnostics in summary view without enabling lifecycle control.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming daemon lifecycle control.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
