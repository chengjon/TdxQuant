# Tasks: Provider Replay Probe Not Requested Targets

## 1. Tests

- [x] 1.1 Add failing provider replay status coverage for default not-requested probe targets.
- [x] 1.2 Add failing provider replay status coverage for partial probe target rollup.
- [x] 1.3 Add failing CLI summary coverage for preserving `probe_summary.not_requested`.

## 2. Implementation

- [x] 2.1 Add `not_requested` list derivation to `_build_provider_replay_probe_summary()`.
- [x] 2.2 Preserve existing probe status, count, requested, healthy, unhealthy, and boundary fields.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming lifecycle management.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.
