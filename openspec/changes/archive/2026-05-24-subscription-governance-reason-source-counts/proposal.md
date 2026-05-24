## Why

B-16/E-09 now expose advisory governance reasons, bounded reason samples, and action rollups, but operators still need to inspect the full `governance.reasons` list to know which subsystems are producing review signals. A compact reason-source count keeps the summary useful for dashboards and registries while preserving the advisory-only boundary.

## What Changes

- Add `governance.reason_source_counts` to subscription long-run status summaries.
- Derive the counts from existing `governance.reasons` prefixes, for example `heartbeat`, `watermark`, `reconnect`, or `overall_status`.
- Project the compact counts through CLI and HTTP summary views without exposing the full raw reasons list.
- Preserve existing observe/manual-review decisions, reason generation, action generation, reconnect/backoff/restart/lifecycle behavior, and event-stream behavior.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: governance summaries include advisory reason-source distribution counts.

## Impact

- Code: `tdxquant/subscription_watch_background.py`, `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Tests: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`, `tests/test_api_cli.py`
- Specs: `openspec/specs/tdx-subscription-long-run-status-summary/spec.md`
- Registry: `FUNCTION_TREE.md` remains the single feature/status registry.
