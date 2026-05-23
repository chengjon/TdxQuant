## 1. Tests

- [x] 1.1 Add governance summary coverage for `requires_manual_review=false` when decision is `observe`.
- [x] 1.2 Add governance summary coverage for `requires_manual_review=true` when resilience state requires review.
- [x] 1.3 Add governance summary coverage for `requires_manual_review=true` when explicit stale inputs require review.

## 2. Implementation

- [x] 2.1 Add `requires_manual_review` to `_build_subscription_watch_governance_summary()`.
- [x] 2.2 Keep existing reasons/actions/decision behavior unchanged.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary without claiming automated reconnect/backoff/restart.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator.
