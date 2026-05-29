# Tasks

## 1. Specification

- [x] 1.1 Add proposal, design, spec deltas, and tasks for explicit restart backoff guard.
- [x] 1.2 Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] 2.1 Add failing background-controller test for replacement start failure writing restart backoff.
- [x] 2.2 Add failing background-controller test for active restart backoff rejecting repeated restart without stop/start.
- [x] 2.3 Add failing preflight and diagnostics tests for `BACKOFF_ACTIVE` projection.

## 3. Implementation

- [x] 3.1 Persist bounded restart backoff metadata after replacement start failure.
- [x] 3.2 Enforce active restart backoff before active-run restart validation.
- [x] 3.3 Project restart backoff through preflight and diagnostics without lifecycle side effects.
- [x] 3.4 Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] 4.1 Run focused tests.
- [x] 4.2 Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] 4.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
