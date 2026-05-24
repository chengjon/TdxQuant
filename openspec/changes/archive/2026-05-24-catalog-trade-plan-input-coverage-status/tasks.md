# Tasks: Catalog Trade Plan Input Coverage Status

## 1. Tests

- [x] 1.1 Add failing catalog summary coverage for missing trade order inputs.
- [x] 1.2 Add failing catalog summary coverage for complete trade order inputs.
- [x] 1.3 Add failing catalog summary coverage for no-input confirm-current plans.

## 2. Implementation

- [x] 2.1 Derive `input_coverage_status` from existing required/provided/missing input fields.
- [x] 2.2 Preserve the existing non-executing boundary metadata, field arrays, counts, and side handling.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary without claiming live-trade readiness.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.
