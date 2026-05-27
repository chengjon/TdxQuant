# provider replay status summary probe advisory fields tasks

## 1. Specification

- [x] Add an OpenSpec delta requiring read-only `summary_view.status_summary` probe advisory fields.
- [x] Validate the active OpenSpec change in strict mode.

## 2. Red Tests

- [x] Add focused CLI summary-view assertions for the new `status_summary` probe advisory fields.
- [x] Run focused tests and confirm the failure is the missing fields.

## 3. Implementation

- [x] Project the fields from existing probe summary/advisory data in `tdxquant/cli.py`.
- [x] Keep probe execution and copied `probe_summary` behavior unchanged.

## 4. Registry and Verification

- [x] Update `FUNCTION_TREE.md` E-06 evidence/boundary notes without claiming readiness or lifecycle management.
- [x] Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] Archive the OpenSpec change, repeat verification, and commit only this slice.
