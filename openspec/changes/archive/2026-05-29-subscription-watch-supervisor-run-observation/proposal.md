## Why

Subscription-watch now supports an explicit bounded foreground supervisor run, but the result is only visible to the caller that invoked it. Operators using later status diagnostics cannot tell whether the latest bounded run waited, recovered, no-oped, or failed without external logs.

## What Changes

- Persist a compact `last_supervisor_run_observation` after bounded foreground supervisor run completes.
- Project that observation through bridge `watch/status?view=diagnostics`.
- Keep the observation compact: tick counts, final status/decision, action flag, bounded tick status/decision counts, and optional run handoff IDs.
- Preserve the boundary: observation only; no scheduling, no background retry, no history ledger, and no raw tick payload exposure.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-task-subscription-watch-background-control`: background control stores latest bounded supervisor-run observation.
- `tdx-worker-bridge-http-control-plane`: diagnostics view exposes compact latest supervisor-run observation.

## Impact

- Code: `tdxquant/subscription_watch_background.py`, `tdxquant/subscription_watch_status_diagnostics.py`.
- Tests: focused background controller and bridge diagnostics tests.
- Registry: `FUNCTION_TREE.md` B-16/E-09 remains `[部分实现]`.

