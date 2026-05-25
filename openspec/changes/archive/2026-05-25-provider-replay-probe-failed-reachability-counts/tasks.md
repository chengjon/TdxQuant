## 1. Specification

- [x] 1.1 Validate the OpenSpec change for failed probe reachability counts.

## 2. Tests and Implementation

- [x] 2.1 Add focused provider replay status tests for empty, healthy-only, failed-unreachable, and mixed probe sets.
- [x] 2.2 Add CLI summary coverage for `probe_summary.failed_reachability_counts`.
- [x] 2.3 Implement failed-only reachability counting in the provider replay probe summary.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming new daemon lifecycle behavior.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator before archive and commit.
