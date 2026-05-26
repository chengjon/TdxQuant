# Add subscription primary evaluated component

## Why

The subscription long-run governance evaluation summary already lists evaluated, stale, fresh, and not-evaluated components, and exposes primary stale/fresh/not-evaluated component hints. It does not expose the first evaluated component directly, so callers that need a compact identity hint must inspect the full `evaluated_components` list.

Adding `primary_evaluated_component` closes that small read-only projection gap without changing heartbeat, watermark, reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

## What Changes

- Add `governance.evaluation_summary.primary_evaluated_component`.
- Derive the field from the first item of `governance.evaluation_summary.evaluated_components`.
- Return `null` when no component has been explicitly evaluated.
- Keep all staleness thresholds, evaluated component ordering, advisory reasons, and actions unchanged.

## Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`

## Impact

- Code: `tdxquant/subscription_watch_background.py`
- Tests: `tests/test_subscription_watch_background.py`
- Specs: `openspec/specs/tdx-subscription-long-run-status-summary/spec.md`
- Registry: `FUNCTION_TREE.md` B-16/E-09 remains `[部分实现]` with explicit evidence and lifecycle boundary.
