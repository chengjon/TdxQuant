# provider replay daemon supervisor loop tasks

## 1. Specification

- [x] Add an OpenSpec delta requiring a foreground managed daemon supervisor loop.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add provider replay helper tests for supervisor heartbeat refresh and child exit observation.
- [x] Add CLI parser/dispatch tests for `provider-replay daemon supervise`.
- [x] Run focused tests and confirm failure is missing supervisor loop support.

## 3. Implementation

- [x] Add managed daemon supervisor helper with injected process/sleep hooks.
- [x] Add child exit and interrupt statefile updates.
- [x] Add CLI parser and dispatch support.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming restart/backoff or real provider control.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
