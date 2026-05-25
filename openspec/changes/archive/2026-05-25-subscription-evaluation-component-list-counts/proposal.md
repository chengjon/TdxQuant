## Why

Subscription governance evaluation summaries already include component list/count fields for evaluated, stale, fresh, and not-evaluated components, but the durable OpenSpec contract only names the fresh and status-count parts. Registering the existing component list/count fields prevents readers from treating them as accidental payload details.

## What Changes

- Add OpenSpec requirements for `evaluation_summary.evaluated_components`, `stale_components`, `not_evaluated_components`, and their count fields.
- Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary to list those fields explicitly.
- Keep behavior unchanged: the fields remain read-only projections derived from explicit staleness evaluation.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`

## Impact

- Affected specs: `openspec/specs/tdx-subscription-long-run-status-summary/spec.md`
- Affected registry: `FUNCTION_TREE.md` B-16/E-09
- Existing test evidence: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`, `tests/test_api_cli.py`
