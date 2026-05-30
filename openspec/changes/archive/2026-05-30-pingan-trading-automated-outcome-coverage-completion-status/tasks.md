## 1. Contract

- [x] 1.1 Add OpenSpec proposal, design, and delta specs for automated outcome coverage completion status.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add a focused failing test for a period report covering confirmed/rejected/failed/exception outcomes.
- [x] 2.2 Confirm the focused test fails because automated coverage completion fields are missing.

## 3. Implementation

- [x] 3.1 Add automated and live/manual completion fields to `acceptance_outcome_coverage_status`.
- [x] 3.2 Preserve read-only report behavior and `acceptance_complete=false` without live/manual evidence.
- [x] 3.3 Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary without changing status.

## 4. Verification

- [x] 4.1 Run focused pytest for trade audit reports and FUNCTION_TREE registry.
- [x] 4.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 4.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
