# Tasks

## 1. Specification

- [x] 1.1 Add proposal, design, spec deltas, and tasks for statefile ownership diagnostics.
- [x] 1.2 Validate the active OpenSpec change in strict mode.

## 2. Tests

- [x] 2.1 Add failing controller tests for missing, owned-active, and mismatch statefile ownership diagnostics.
- [x] 2.2 Add failing bridge diagnostics test for compact `statefile_ownership` projection.

## 3. Implementation

- [x] 3.1 Implement read-only statefile ownership diagnostic derivation.
- [x] 3.2 Include `statefile_ownership` in controller status and bridge diagnostics view.
- [x] 3.3 Update FUNCTION_TREE B-16/E-09 evidence and boundary while keeping `[部分实现]`.

## 4. Verification

- [x] 4.1 Run focused tests.
- [x] 4.2 Run OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] 4.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
