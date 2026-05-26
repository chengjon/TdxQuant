# Tasks

## 1. Contract

- [x] 1.1 Add OpenSpec proposal, design, and provider replay delta for error-sample reachability counts.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Tests

- [x] 2.1 Add detailed provider replay assertions for `runtime.probe_summary.error_sample_reachability_counts` and key count.
- [x] 2.2 Add CLI summary-view assertions that projected `probe_summary` includes those fields.

## 3. Implementation

- [x] 3.1 Derive `error_sample_reachability_counts` from existing error sample candidates.
- [x] 3.2 Derive `error_sample_reachability_key_count` from that count map.

## 4. Registry and Verification

- [x] 4.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming daemon lifecycle support.
- [x] 4.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator before archive and commit.
