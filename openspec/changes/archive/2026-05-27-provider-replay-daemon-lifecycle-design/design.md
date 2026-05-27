# provider replay daemon lifecycle design

## Context

The current provider replay service can serve fake provider HTTP endpoints and can inspect an already-running replay process through read-only probes. It does not own a daemon process, maintain pidfiles, supervise restarts, or apply retry/backoff policy.

This design records the future lifecycle control boundary so later implementation can be reviewed against an explicit contract instead of accreting lifecycle behavior through status/probe commands.

## Current State

- `provider-replay serve --config` can run a foreground replay HTTP server.
- `provider-replay status --config` builds a read-only lifecycle boundary payload.
- `provider-replay status --probe-*` can optionally probe an already-running replay service.
- `provider-replay status --view summary` projects read-only lifecycle, capability, and probe metadata.
- Lifecycle fields intentionally report no managed lifecycle support:
  - `start_stop_managed=false`
  - `daemon_managed=false`
  - `scheduler_managed=false`
  - `restart_policy=not_managed`
  - `control_supported=false`
  - `managed_operation_count=0`

## Future Lifecycle Contract

### Start

A future lifecycle controller may start provider replay only from an explicit config path and an explicit operator command. It must record enough ownership metadata to distinguish processes it owns from arbitrary already-running replay services.

Start must not silently reuse live trading provider credentials or imply broker readiness. It starts a replay fake provider, not a live provider bridge.

### Stop

Stop may only target a process that the lifecycle controller can prove it owns, such as through a future pidfile/statefile with matching provider/config identity. It must not kill arbitrary processes discovered by port probing.

Stop must report when a matching owned process is absent rather than treating an unrelated process as controllable.

### Lifecycle Status

Lifecycle status must distinguish:

- configured replay capability
- owned daemon process state
- observed HTTP health/probe state
- stale or missing ownership metadata

Status must remain safe to run without mutating state. A reachable probe alone is not proof that the lifecycle controller owns the process.

### Restart

Restart must be explicit lifecycle control: stop an owned replay process and start it again from the same validated config. It must not be triggered by read-only status, summary, probe, or catalog discovery commands.

If restart cannot prove ownership, it must fail closed and report the ownership boundary.

### Backoff

Backoff policy belongs to future supervised restart behavior, not to current status/probe code. A future policy must expose retry count, delay window, last failure reason, and whether the next retry is pending or blocked.

Backoff defaults should be non-aggressive and bounded. Automatic restart/backoff must be opt-in and must not be implied by the current provider-replay status surface.

## Non-Goals

- Implementing start/stop/restart commands in this change
- Adding pidfile/statefile writes in this change
- Adding a supervisor loop or scheduler in this change
- Adding automatic reconnect/backoff in this change
- Mutating provider state, watchlists, orders, or live broker state
- Proving broker readiness, live market availability, or workflow readiness

## Acceptance Boundary

This change is complete when the lifecycle design and spec boundaries are registered, `FUNCTION_TREE.md` clearly marks lifecycle control as designed/pending within E-06, and validation passes. Runtime behavior must remain unchanged.

