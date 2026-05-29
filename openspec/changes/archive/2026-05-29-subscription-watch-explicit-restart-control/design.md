# Design: Explicit Subscription Watch Restart

## Scope

This change adds a manual restart operation for the worker-local subscription-watch background controller. It is triggered only by explicit operator action through the controller, HTTP route, registry helper, or CLI command.

## Restart Semantics

`restart(reason=None, grace_period_seconds=None)` SHALL:

1. Read and reconcile the current active control state.
2. Require an active run with a persisted `start_request`.
3. Stop the currently owned run using existing stop semantics.
4. Start a replacement run using the persisted `start_request`.
5. Return a restart envelope:
   - `status`: `restarted`
   - `previous_run_id`
   - `new_run_id`
   - `stop_result`
   - `start_result`
   - `start_request`
   - `reason`

If no active run exists, restart SHALL return `NO_ACTIVE_RUN`. If the active state has no valid `start_request`, restart SHALL return `MISSING_START_REQUEST`. If stop fails, restart SHALL return that failure and MUST NOT start a replacement run.

## HTTP and CLI Shape

- HTTP: `POST /bridge/v1/watch/restart`
- CLI: `bridge watch-restart --registry ... --worker ... [--reason ...] [--grace-period-seconds ...]`
- Registry helper: `run_bridge_watch_restart(...)`

## Non-goals

- No automatic restart, retry timer, backoff scheduler, or supervisor loop.
- No restart policy.
- No readiness gate or health proof.
- No PID ownership model change beyond existing stop/start checks.
- No changes to event-stream/SSE behavior.
