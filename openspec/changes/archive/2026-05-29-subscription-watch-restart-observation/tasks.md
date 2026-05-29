# Tasks

## 1. Specification

- [x] 1.1 Add proposal, design, spec deltas, and tasks for explicit restart observation.
- [x] 1.2 Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] 2.1 Add failing background-controller test for persisted successful restart observation.
- [x] 2.2 Add failing HTTP diagnostics test for restart observation projection.
- [x] 2.3 Add failing CLI diagnostics test for restart observation projection.

## 3. Implementation

- [x] 3.1 Persist latest successful explicit restart observation on replacement active state.
- [x] 3.2 Add diagnostics restart observation derivation without exposing raw control payloads.
- [x] 3.3 Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] 4.1 Run focused tests.
- [x] 4.2 Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] 4.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
