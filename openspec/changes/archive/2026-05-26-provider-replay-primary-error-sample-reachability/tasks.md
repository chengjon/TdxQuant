# Tasks

## 1. Contract

- [x] 1.1 Add OpenSpec proposal, design, and provider replay delta for primary error sample reachability.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Tests

- [x] 2.1 Add detailed provider replay assertions for `runtime.probe_summary.primary_error_sample_reachability`.
- [x] 2.2 Add CLI summary-view assertions that projected `probe_summary` includes the field.

## 3. Implementation

- [x] 3.1 Derive `primary_error_sample_reachability` from the first error sample candidate.
- [x] 3.2 Preserve existing `error_samples` payload shape and ordering.

## 4. Registry and Verification

- [x] 4.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming daemon lifecycle support.
- [x] 4.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator before archive and commit.
