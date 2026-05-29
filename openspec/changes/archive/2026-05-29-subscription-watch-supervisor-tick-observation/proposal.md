## Why

The explicit subscription-watch supervisor tick already returns a compact decision, but that decision disappears after the call unless the caller captures it immediately. Operators need the latest manual tick outcome to be visible through the existing statefile and diagnostics path without implying that a background supervisor or provider lifecycle manager is running.

## What Changes

- Persist a compact `last_supervisor_tick_observation` after an explicit `supervisor_tick()` call when an existing control statefile can hold it.
- Project that observation through bridge `watch/status?view=diagnostics`.
- Keep the observation compact: status, decision, action flag, reason codes, optional run handoff IDs, optional start-request summary, reason, and boundary.
- Preserve the boundary: observation only; no background loop, no automatic scheduling, no provider readiness claim, no lifecycle ownership proof, and no raw tick payload exposure.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-task-subscription-watch-background-control`: persist the latest compact supervisor-tick observation on existing control state.
- `tdx-worker-bridge-http-control-plane`: expose the latest compact supervisor-tick observation in diagnostics view when present.

## Impact

- Affected code: `tdxquant/subscription_watch_background.py`, `tdxquant/subscription_watch_status_diagnostics.py`.
- Affected tests: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`.
- Affected registry/specs: `FUNCTION_TREE.md`, background-control OpenSpec, worker-bridge OpenSpec.
