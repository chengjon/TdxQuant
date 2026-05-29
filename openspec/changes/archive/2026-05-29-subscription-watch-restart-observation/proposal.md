## Why

Explicit subscription-watch restart is now available, but its successful handoff is only visible in the immediate restart response. Operators need a stable read-only observation in later status diagnostics so they can tell which active run replaced which prior run without inferring from logs or process arguments.

## What Changes

- Persist a compact `last_restart_observation` after an explicit restart successfully stops an active run and starts a replacement.
- Include the same compact observation in the restart response and detailed control state.
- Project the observation into `watch-status --view diagnostics` and worker bridge diagnostics as a read-only summary.
- Keep the boundary explicit: no automatic restart, no backoff scheduler, no supervisor loop, no ownership proof, and no health/readiness claim.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-task-subscription-watch-background-control`: explicit restart records a compact successful restart observation.
- `tdx-subscription-long-run-status-summary`: diagnostics view exposes the compact restart observation when present.
- `tdx-worker-bridge-http-control-plane`: worker bridge diagnostics preserves the restart observation summary without triggering lifecycle control.

## Impact

- Code: `tdxquant/subscription_watch_background.py`, `tdxquant/subscription_watch_status_diagnostics.py`, `tdxquant/bridge_http.py`, `tdxquant/cli.py`.
- Tests: focused subscription background, bridge HTTP, and CLI diagnostics tests.
- Docs/registry: `FUNCTION_TREE.md` B-16/E-09 evidence and boundary remain `[部分实现]`.
