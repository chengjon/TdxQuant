## Context

`ProviderTransportReplayHTTPServer` serves `/provider/v1/replay/watch/events` from fixtures. The existing status command can now optionally probe `/health` and `/watch/status`, but not the replay event list endpoint.

This change extends the same passive status model. It only performs an explicit HTTP GET against an already-running replay service and reports whether the event projection looks reachable.

## Goals / Non-Goals

**Goals:**

- Probe `/provider/v1/replay/watch/events` with the configured token and timeout.
- Report normalized probe status under `runtime.watch_events_probe`.
- Mark `runtime.runtime_observed` true if any explicit runtime probe is enabled.
- Preserve all no-daemon-management and read-only boundaries.

**Non-Goals:**

- No service startup, process discovery, restart, or scheduler.
- No mutation/write probing.
- No SSE/event-stream probe in this slice.
- No fixture contract changes.

## Decisions

- Keep `watch_events_probe` separate from health and watch-status probes.
  - Rationale: event projection reachability is stronger than health but distinct from status projection reachability.
- Treat HTTP 200 with a JSON `result.events` array as healthy.
  - Rationale: this verifies the fake provider event surface without validating individual event semantics.
- Use the existing `--probe-timeout`.
  - Rationale: probe behavior remains simple and consistent across provider replay status probes.

## Risks / Trade-offs

- Another probe option increases CLI surface area.
  - Mitigation: it follows the already established `--probe-*` pattern and stays opt-in.
- Operators may confuse probe failure with daemon failure.
  - Mitigation: `FUNCTION_TREE.md` and status lifecycle boundaries continue to state no daemon/start-stop/restart management exists.
