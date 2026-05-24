# Tasks: Subscription Summary Fresh Evaluation Counts

## 1. Tests

- [x] 1.1 Add failing coverage for default not-evaluated summaries with zero fresh components.
- [x] 1.2 Add failing coverage for mixed fresh/stale component summaries.
- [x] 1.3 Add failing coverage for reconnect-stale summaries preserving heartbeat/watermark fresh counts.

## 2. Implementation

- [x] 2.1 Derive `fresh_components` and `fresh_count` in the existing evaluation summary helper.
- [x] 2.2 Preserve governance decision, reason/action generation, and advisory-only behavior.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary without claiming lifecycle automation.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.
