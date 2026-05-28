# provider replay lifecycle statefile boundary tasks

## 1. Specification

- [x] Add an OpenSpec delta requiring read-only lifecycle statefile boundary reporting.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add focused provider replay config/status assertions for `lifecycle_state_file` and `lifecycle.statefile_summary`.
- [x] Add API CLI config-check summary assertions for non-inspecting statefile fields.
- [x] Run focused tests and confirm the failure is the missing statefile boundary.

## 3. Implementation

- [x] Parse optional `lifecycle_state_file` into provider replay config.
- [x] Add read-only `lifecycle.statefile_summary` without filesystem inspection or lifecycle control.
- [x] Add config-check summary statefile boundary fields without starting/probing/inspecting runtime.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming daemon lifecycle control.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
