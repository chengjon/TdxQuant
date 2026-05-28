# provider replay managed daemon control tasks

## 1. Specification

- [x] Add an OpenSpec delta requiring managed daemon start/status/stop.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add provider replay helper tests for managed start, status, stop, and already-running protection.
- [x] Add CLI parser/dispatch tests for `provider-replay daemon start|status|stop`.
- [x] Run focused tests and confirm failure is missing managed daemon control.

## 3. Implementation

- [x] Add process liveness, launch, terminate, and command-building helpers.
- [x] Add managed daemon start/status/stop helpers using statefile ownership.
- [x] Add CLI parser and dispatch support.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming supervisor or restart/backoff.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
