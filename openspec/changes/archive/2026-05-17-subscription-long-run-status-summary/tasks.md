## 1. Status Summary

- [x] 1.1 Add a pure summary builder for subscription-watch background control/status payloads.
- [x] 1.2 Include the summary in `SubscriptionWatchBackgroundController.status()` without changing raw fields.

## 2. Registry And Verification

- [x] 2.1 Update `FUNCTION_TREE.md` from designed/pending to partially implemented with status-summary boundaries.
- [x] 2.2 Add focused tests for stopped, running, and reconnecting/degraded status summary payloads.
- [x] 2.3 Run focused tests, OpenSpec strict validation, `git diff --check`, and the `FUNCTION_TREE.md` registry validator.
