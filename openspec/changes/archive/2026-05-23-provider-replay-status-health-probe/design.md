## Context

The provider replay service already exposes `/provider/v1/replay/health`, and `provider-replay status --config` already reports static replay-only lifecycle boundaries. That status intentionally does not start a socket or observe runtime health, which keeps the boundary clear but makes it less useful when a foreground replay service is already running.

## Goals / Non-Goals

**Goals:**

- Add explicit, read-only health probing for the configured replay HTTP service.
- Preserve the default `status --config` behavior as static and network-free.
- Make probe output clear enough to distinguish replay-service reachability from managed daemon health.

**Non-Goals:**

- No daemon start/stop/restart lifecycle management.
- No scheduler, backoff, or watchdog behavior.
- No live provider or live market session probing.
- No token disclosure in status output.

## Decisions

- Add a small `probe_provider_transport_replay_health(config, timeout_seconds=...)` helper using the standard library HTTP client.
  - Rationale: the repo already uses standard library HTTP for replay tests and service code, and no new dependency is needed.
- Keep `build_provider_transport_replay_status(config, health_probe=None)` pure by accepting an optional probe result instead of performing network I/O internally.
  - Rationale: default status remains deterministic and testable without sockets.
- Add `provider-replay status --probe-health` and `--probe-timeout`.
  - Rationale: probing is visible and opt-in; timeout is bounded and caller-controlled.
- Report probe output under `runtime.health_probe` and keep `lifecycle.start_stop_managed=false`.
  - Rationale: the result observes the replay HTTP service only, not daemon ownership.

## Risks / Trade-offs

- A healthy replay health endpoint may be mistaken for daemon management. Mitigate with explicit `start_stop_managed=false`, `daemon_managed=false`, and boundary text.
- A local probe can fail because the service is not running or the token/allowlist is wrong. Mitigate by returning structured `unreachable`/`error` metadata rather than raising during status generation.
- Very short timeouts may produce false negatives. Mitigate by exposing the timeout in the probe result.
