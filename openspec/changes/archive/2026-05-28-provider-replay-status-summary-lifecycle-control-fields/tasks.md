# provider replay status summary lifecycle control fields tasks

## 1. Specification

- [x] Add an OpenSpec delta requiring read-only `summary_view.status_summary` lifecycle ownership/control fields.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add focused CLI summary-view assertions for the new `status_summary` lifecycle fields.
- [x] Run focused tests and confirm the failure is the missing fields.

## 3. Implementation

- [x] Project the fields from existing lifecycle ownership/control summaries in `tdxquant/cli.py`.
- [x] Keep lifecycle control, probes, and detailed summary behavior unchanged.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming daemon lifecycle control.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
