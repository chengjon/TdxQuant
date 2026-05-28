# Tasks

## 1. Specification

- [x] Add proposal, design, spec delta, and tasks for reconnect governance rollup.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] Add a failing core status-summary assertion for `governance.reconnect_rollup`.
- [x] Add failing HTTP summary-view assertions for `governance.reconnect_rollup`.
- [x] Add failing CLI summary-view assertions for `governance.reconnect_rollup`.
- [x] Confirm focused tests fail because the rollup is missing.

## 3. Implementation

- [x] Add core reconnect rollup derivation from existing reconnect diagnostics.
- [x] Project reconnect rollup through HTTP summary view.
- [x] Project reconnect rollup through CLI summary view.
- [x] Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] Run focused tests.
- [x] Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
