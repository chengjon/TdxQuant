# submit-once task plan preview boundary registry tasks

## 1. Specification

- [x] Add OpenSpec proposal/design/spec/tasks for D-08 read-only submit-once task plan/preview registration.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add focused API CLI tests for `task-buy-submit-once` and `task-sell-submit-once` catalog plan/preview summary boundaries.
- [x] Add a focused FUNCTION_TREE registry assertion for D-08 plan/preview evidence and non-execution wording.
- [x] Run the focused registry test and confirm it fails because D-08 evidence is stale.

## 3. Registry Update

- [x] Update `FUNCTION_TREE.md` D-08 evidence to cite buy/sell submit-once task plan/preview boundaries.
- [x] Keep D-08 `[部分实现]` and preserve boundaries for catalog run, desktop primitives, readiness, safety, and exception coverage.

## 4. Verification

- [x] Run focused API CLI and FUNCTION_TREE registry tests.
- [x] Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this D-08 slice.
