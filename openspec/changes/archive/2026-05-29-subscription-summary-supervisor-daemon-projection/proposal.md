## Why

Subscription-watch long-run status already exposes top-level `supervisor_daemon` status, but `status_summary` and summary views do not carry a stable compact projection of that daemon read model. Operators using summary output have to switch back to detailed payloads to see whether the explicit supervisor daemon is missing, running, stale, or blocked by local state evidence.

## What Changes

- Add an additive read-only `status_summary.supervisor_daemon` projection derived from the existing supervisor daemon status result.
- Include the same compact daemon projection in bridge `watch-status --view summary` output under `status_summary.supervisor_daemon`.
- Preserve the existing top-level detailed `supervisor_daemon` payload and all lifecycle behavior.
- Do not start, stop, restart, supervise, backoff, probe, or mutate provider state as part of summary construction.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: add a stable read-only supervisor daemon projection to `status_summary` and summary views.

## Impact

- Affected code: `tdxquant/subscription_watch_background.py`, `tdxquant/cli.py`.
- Affected tests: `tests/test_subscription_watch_background.py`, `tests/test_api_cli.py`.
- Affected registry: `FUNCTION_TREE.md` B-16/E-09 evidence and boundary.
- No new runtime dependency, provider mutation, scheduler, daemon lifecycle default, or trading behavior.
