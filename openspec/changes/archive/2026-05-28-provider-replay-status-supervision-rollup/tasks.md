# provider replay status supervision rollup tasks

## 1. Specification

- [x] Add an OpenSpec delta requiring read-only supervision fields in `summary_view.status_summary`.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add focused API CLI summary-view assertions for supervision rollup fields.
- [x] Run focused tests and confirm the failure is the missing status summary fields.

## 3. Implementation

- [x] Derive supervision rollup fields from `lifecycle.supervision_summary`.
- [x] Preserve the detailed status payload and nested lifecycle summary without adding lifecycle control.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming daemon lifecycle control.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
