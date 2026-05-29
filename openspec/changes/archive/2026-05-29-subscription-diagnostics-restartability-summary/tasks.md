# Tasks

## 1. Specification

- [x] Add proposal, design, spec deltas, and tasks for diagnostics restartability summary.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] Add failing HTTP diagnostics test for restartability summary.
- [x] Add failing CLI diagnostics test for restartability summary.
- [x] Add failing blocked diagnostics restartability reason test.

## 3. Implementation

- [x] Add diagnostics restartability derivation.
- [x] Thread detailed status payload into HTTP and CLI diagnostics builders without exposing raw payload.
- [x] Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] Run focused tests.
- [x] Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
