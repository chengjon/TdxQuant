# submit-once bundle boundary summary registry tasks

## 1. Specification

- [x] Add OpenSpec proposal/design/spec/tasks for D-08 read-only bundle boundary summary registration.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add focused API CLI tests for buy/sell submit-once bundle plan/preview boundary rollup fields.
- [x] Add a focused FUNCTION_TREE registry assertion for D-08 bundle rollup evidence and non-execution wording.
- [x] Run the focused tests and confirm failure before implementation/registry update.

## 3. Implementation

- [x] Add additive bundle summary rollup fields derived from selected step `trade_plan_boundary` values.
- [x] Mirror the rollup into `plan_summary` via selected step summary.

## 4. Registry Update

- [x] Update `FUNCTION_TREE.md` D-08 evidence to cite buy/sell submit-once bundle plan/preview boundary rollups.
- [x] Keep D-08 `[部分实现]` and preserve boundaries for catalog run, desktop primitives, readiness, safety, and exception coverage.

## 5. Verification

- [x] Run focused API CLI and FUNCTION_TREE registry tests.
- [x] Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this D-08 slice.
