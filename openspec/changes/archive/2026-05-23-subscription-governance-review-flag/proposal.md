## Why

B-16/E-09 now expose advisory `governance.decision`, reasons, and actions. Callers that only need to know whether human review is required still have to compare the `decision` string.

Adding a stable `requires_manual_review` boolean keeps the status projection easier to consume while preserving the current advisory-only boundary.

## What Changes

- Add `governance.requires_manual_review` to `status_summary`.
- Set it to `false` when governance decision is `observe`.
- Set it to `true` when governance decision is `manual_review`.
- Preserve existing `decision`, `reasons`, `actions`, `staleness_evaluated`, and boundary fields.
- Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary without claiming automated reconnect/backoff/restart.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: expose a boolean manual-review flag in the advisory governance summary.

## Impact

- Runtime code: `tdxquant/subscription_watch_background.py`
- Tests: `tests/test_subscription_watch_background.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-subscription-long-run-status-summary/spec.md`
