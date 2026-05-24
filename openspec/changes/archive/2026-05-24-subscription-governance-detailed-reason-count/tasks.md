# Tasks: Subscription Governance Detailed Reason Count

## 1. Tests

- [x] 1.1 Add detailed status-summary tests for observe and manual-review `governance.reason_count`.
- [x] 1.2 Confirm summary-view `reason_count` remains compatible with the detailed reasons list.

## 2. Implementation

- [x] 2.1 Add `reason_count` to `_build_subscription_watch_governance_summary()`.
- [x] 2.2 Keep the field derived from `governance.reasons` only.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` B-16 evidence and boundary without claiming automatic reconnect/backoff control.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, GitNexus change detection, and the FUNCTION_TREE validator.
