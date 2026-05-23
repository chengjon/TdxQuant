## Why

B-16 and E-09 already expose heartbeat, watermark, reconnect, and degraded state diagnostics, but operators still need a compact read-only signal that explains whether the current snapshot is only observable or deserves manual review. Without that field, downstream bridge/CLI consumers have to infer governance posture from several sub-objects.

## What Changes

- Add a `governance` sub-object to `status_summary`.
- The object reports an advisory decision (`observe` or `manual_review`), machine-readable reasons, whether stale inputs were explicitly evaluated, and an advisory-only boundary string.
- Mark reconnecting/degraded/failed states and explicitly stale heartbeat/watermark diagnostics as manual-review reasons.
- Preserve the existing lifecycle boundary: no automatic restart, reconnect, backoff, or event-stream behavior changes.
- Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: expose an advisory governance summary inside the existing status projection.

## Impact

- Runtime code: `tdxquant/subscription_watch_background.py`
- Tests: `tests/test_subscription_watch_background.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-subscription-long-run-status-summary/spec.md`
