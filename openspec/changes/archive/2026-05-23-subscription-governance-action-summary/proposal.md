## Why

E-09/B-16 now expose read-only long-run status, stale diagnostics, and an advisory `governance.decision`. Operators can see why a subscription-watch run needs review, but callers still have to infer what kind of review is needed from free-form reason strings.

Adding explicit advisory action hints makes the status projection easier to automate around while preserving the current boundary: no reconnect, restart, backoff, lifecycle, or event-stream behavior changes.

## What Changes

- Add a stable `governance.actions` list to `status_summary`.
- Keep `governance.actions=[]` when the decision is `observe`.
- Emit deterministic advisory actions for resilience-state reasons and explicit stale heartbeat/watermark inputs.
- Preserve the existing `governance.decision`, `governance.reasons`, `staleness_evaluated`, and advisory-only boundary.
- Update `FUNCTION_TREE.md` E-09/B-16 evidence and boundary without claiming automated long-run governance.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: expose advisory governance action hints in the long-run status summary.

## Impact

- Runtime code: `tdxquant/subscription_watch_background.py`
- Tests: `tests/test_subscription_watch_background.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-subscription-long-run-status-summary/spec.md`
