# Tasks: Provider Replay Probe Total Count

## 1. Tests

- [x] 1.1 Add detailed status tests for `runtime.probe_summary.total_count`.
- [x] 1.2 Add CLI summary-view coverage that preserves `probe_summary.total_count`.

## 2. Implementation

- [x] 2.1 Add `total_count` to `_build_provider_replay_probe_summary()`.
- [x] 2.2 Keep `total_count` derived from `PROVIDER_REPLAY_STATUS_PROBE_KEYS`.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming daemon lifecycle management.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.
