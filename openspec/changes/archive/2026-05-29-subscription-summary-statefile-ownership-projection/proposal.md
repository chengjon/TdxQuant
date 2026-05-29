## Why

Subscription-watch detailed status already exposes `statefile_ownership`, but summary consumers cannot see whether the active control state is absent, locally owned, or mismatched without requesting the detailed payload. This leaves a gap in B-16/E-09 long-run governance observability for operators who rely on compact summary views.

## What Changes

- Add an additive read-only `status_summary.statefile_ownership` projection derived from the existing background statefile ownership diagnostic.
- Include the same compact ownership projection in bridge `watch-status --view summary` output under `status_summary.statefile_ownership`.
- Preserve the existing top-level detailed `statefile_ownership` payload and all lifecycle behavior.
- Do not acquire locks, start, stop, restart, supervise, backoff, probe, or mutate provider state as part of summary construction.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: add a stable read-only statefile ownership projection to `status_summary` and summary views.

## Impact

- Affected code: `tdxquant/subscription_watch_background.py`, `tdxquant/cli.py`.
- Affected tests: `tests/test_subscription_watch_background.py`, `tests/test_api_cli.py`.
- Affected registry: `FUNCTION_TREE.md` B-16/E-09 evidence and boundary.
- No new runtime dependency, provider mutation, scheduler, daemon lifecycle default, or trading behavior.
