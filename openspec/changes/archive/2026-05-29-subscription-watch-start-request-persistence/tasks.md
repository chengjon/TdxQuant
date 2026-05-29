# Tasks

## 1. Specification

- [x] Add proposal, design, spec delta, and tasks for start request persistence.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] Add failing test that start persists `start_request` in active state/result.
- [x] Add failing test that same-idempotency replay returns the original persisted `start_request`.

## 3. Implementation

- [x] Persist normalized start request metadata when writing active state.
- [x] Preserve start request metadata through idempotent replay/status reads.
- [x] Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] Run focused tests.
- [x] Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
