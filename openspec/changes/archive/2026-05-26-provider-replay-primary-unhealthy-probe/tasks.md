# Tasks

## 1. Contract

- [x] 1.1 Add OpenSpec proposal, design, and provider transport replay delta for `primary_unhealthy_probe`.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Tests

- [x] 2.1 Add provider replay status assertions for null and populated `primary_unhealthy_probe`.
- [x] 2.2 Add or update CLI summary-view assertions showing the field is projected without exposing new lifecycle behavior.

## 3. Implementation

- [x] 3.1 Derive `runtime.probe_summary.primary_unhealthy_probe` from the existing `unhealthy` list.

## 4. Registry and Verification

- [x] 4.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming daemon lifecycle management.
- [x] 4.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator before archive and commit.
