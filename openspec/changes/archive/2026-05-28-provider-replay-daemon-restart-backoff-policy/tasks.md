# provider replay daemon restart backoff policy tasks

## 1. Specification

- [x] Add an OpenSpec delta requiring opt-in supervisor restart/backoff.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add provider replay helper tests for on-failure restart with backoff and final success.
- [x] Add provider replay helper tests for restart exhaustion and failed statefile recording.
- [x] Add CLI parser/dispatch tests for restart policy options.
- [x] Run focused tests and confirm failure is missing restart/backoff support.

## 3. Implementation

- [x] Extend supervisor helper with restart policy, max restart, and backoff parameters.
- [x] Record backoff and failed lifecycle states.
- [x] Add CLI parser and dispatch support for restart/backoff options.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming full lifecycle completion or real provider control.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
