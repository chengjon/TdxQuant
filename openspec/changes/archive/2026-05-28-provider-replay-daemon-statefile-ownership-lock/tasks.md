# provider replay daemon statefile ownership lock tasks

## 1. Specification

- [x] Add an OpenSpec delta requiring locked atomic lifecycle statefile writes.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add statefile writer coverage for ownership payload fields and read-back diagnostics.
- [x] Add lock exclusion coverage proving an existing lock blocks writes and preserves the old statefile.
- [x] Run focused tests and confirm failure is missing writer/diagnostic fields.

## 3. Implementation

- [x] Add lifecycle state payload and config-hash helpers.
- [x] Add exclusive lock and atomic statefile writer.
- [x] Extend read-only diagnostics to report optional owner token, generation, and config hash match.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming daemon lifecycle control.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
