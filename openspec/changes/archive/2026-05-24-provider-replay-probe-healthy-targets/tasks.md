## 1. Tests

- [x] 1.1 Add provider replay status coverage for empty `runtime.probe_summary.healthy` when no probes are requested.
- [x] 1.2 Add provider replay status coverage for populated `runtime.probe_summary.healthy` when probes are healthy.
- [x] 1.3 Add CLI summary-view coverage that carries `probe_summary.healthy`.

## 2. Implementation

- [x] 2.1 Add deterministic healthy target aggregation to provider replay probe summary construction.
- [x] 2.2 Preserve existing requested/unhealthy/count fields and read-only lifecycle boundaries.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming daemon lifecycle management.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.
