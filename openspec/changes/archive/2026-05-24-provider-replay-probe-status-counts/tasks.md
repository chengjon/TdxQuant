## 1. Tests

- [x] 1.1 Add provider replay status coverage for `probe_summary.status_counts` when no probes are requested.
- [x] 1.2 Add provider replay status/CLI summary coverage for `probe_summary.status_counts` when probes are requested.

## 2. Implementation

- [x] 2.1 Add deterministic probe status count aggregation to `_build_provider_replay_probe_summary()`.
- [x] 2.2 Preserve existing probe summary fields and lifecycle boundaries.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming daemon lifecycle management.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.
