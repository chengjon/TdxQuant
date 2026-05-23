## Context

`ProviderTransportReplayHTTPServer` already serves health, fixture catalog, watch status, watch events, and watch event stream endpoints. `provider-replay status --probe-health` can observe a running replay service, but it only checks `/health`.

This change adds a second explicit probe for the watch-status fake provider projection. The status command remains passive: it loads config, optionally probes an already-running HTTP endpoint, and reports the result.

## Goals / Non-Goals

**Goals:**

- Probe `/provider/v1/replay/watch/status` with the configured token and timeout.
- Report normalized probe status under `runtime.watch_status_probe`.
- Keep `runtime.runtime_observed` true if either health or watch-status probing is enabled.
- Preserve existing no-daemon-management boundaries.

**Non-Goals:**

- No service startup or process discovery.
- No background daemon, scheduler, restart, or backoff policy.
- No mutation/write endpoint probing.
- No change to replay fixture contract or SSE/event-stream semantics.

## Decisions

- Keep watch-status probe separate from health probe.
  - Rationale: callers may want either a cheap health probe or a stronger fake-provider-surface probe.
- Reuse the existing bearer-token HTTP probe style.
  - Rationale: endpoint auth behavior stays consistent with current replay service tests and implementation.
- Store the result under `runtime.watch_status_probe`.
  - Rationale: the probe observes runtime reachability, not config shape or lifecycle management.

## Risks / Trade-offs

- A failed watch-status probe could be mistaken for daemon failure.
  - Mitigation: status text remains probe-scoped, and lifecycle boundaries continue to say start/stop/restart are unmanaged.
- Extra probe increases status latency when requested.
  - Mitigation: it is opt-in and uses the existing `--probe-timeout`.
