# pingan bundle boundary command summary registry tasks

## 1. Specification

- [x] Add OpenSpec proposal/design/spec/tasks for D-07 read-only bundle command rollup registration.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add focused API CLI tests for buy/sell/confirm_current PingAn bundle plan/preview command rollup fields.
- [x] Add a focused FUNCTION_TREE registry assertion for D-07 bundle command rollup evidence and non-execution wording.
- [x] Run the focused tests and confirm failure before implementation/registry update.

## 3. Implementation

- [x] Add additive bundle summary command rollup fields derived from selected step `trade_plan_boundary.trade_command` values.
- [x] Mirror the rollup into `selected_step_summary` and `plan_summary`.

## 4. Registry Update

- [x] Update `FUNCTION_TREE.md` D-07 evidence to cite buy/sell/confirm_current bundle plan/preview command rollups.
- [x] Keep D-07 `[部分实现]` and preserve boundaries for catalog run, desktop primitives, readiness, safety, and exception coverage.

## 5. Verification

- [x] Run focused API CLI and FUNCTION_TREE registry tests.
- [x] Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this D-07 slice.
