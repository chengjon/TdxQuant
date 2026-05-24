# Tasks: Provider Replay Probe Unhealthy Count

## 1. Tests

- [x] 1.1 Add focused failing tests for detailed `probe_summary.unhealthy_count`.
- [x] 1.2 Add summary-view assertions that preserve `probe_summary.unhealthy_count`.

## 2. Implementation

- [x] 2.1 Add `unhealthy_count` to `_build_provider_replay_probe_summary()`.
- [x] 2.2 Keep `unhealthy_count` derived from the existing unhealthy target list and compatible with `failed_count`.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming daemon lifecycle management.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.
