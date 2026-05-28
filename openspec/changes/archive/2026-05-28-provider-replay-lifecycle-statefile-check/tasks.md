# provider replay lifecycle statefile check tasks

## 1. Specification

- [x] Add an OpenSpec delta requiring read-only lifecycle statefile schema/staleness checks.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add provider replay helper tests for valid, stale, missing, and not-configured statefile checks.
- [x] Add CLI parser and dispatch tests for detailed and summary lifecycle-state-check output.
- [x] Run focused tests and confirm the failure is the missing statefile check command/helper.

## 3. Implementation

- [x] Add a read-only statefile check helper with schema, provider-id, and staleness diagnostics.
- [x] Add CLI parser support for `provider-replay lifecycle-state-check`.
- [x] Add detailed and summary output without lifecycle control, runtime probing, or statefile writes.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming daemon lifecycle control.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
