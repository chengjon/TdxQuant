## 1. Summary Tests

- [x] 1.1 Add tests for governance `observe` posture when no stale threshold is provided.
- [x] 1.2 Add tests for governance `manual_review` posture on reconnecting/degraded/failed states.
- [x] 1.3 Add tests for governance stale heartbeat/watermark reasons when thresholds are explicit.

## 2. Runtime Implementation

- [x] 2.1 Add a helper that builds advisory governance from overall status, heartbeat summary, and watermark summary.
- [x] 2.2 Include `governance` in `build_subscription_watch_status_summary()` without changing lifecycle behavior.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary without claiming automatic reconnect/backoff.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator.
