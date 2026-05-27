# provider replay health summary presence flags design

## Context

E-06 is intentionally still `[部分实现]`: provider replay is a foreground, replay-only fake provider with read-only status/config/probe inspection. Existing status payloads include full sibling probe rollups and a nested `health_summary`, but the nested object lacks direct booleans for common presence checks.

## Design

Extend `_build_provider_replay_probe_summary()` so `health_summary` includes:

- `has_healthy_probe`: `True` when the normalized healthy probe list is non-empty.
- `has_failed_probe`: `True` when the normalized failed probe count/list is non-empty.
- `has_unhealthy_probe`: `True` when the normalized unhealthy probe list is non-empty.

The fields are derived from the same in-memory rollup data already used for sibling fields. No CLI dispatch, HTTP probing, socket lifecycle, fixture loading, daemon management, or provider write path changes are required.

The CLI summary view already copies the detailed `probe_summary`, so it should expose the new nested fields without an additional projection layer.

## Boundaries

- This change is read-only status metadata.
- It does not execute extra probes or make unrequested endpoints observable.
- It does not start, stop, restart, daemonize, schedule, supervise, or back off provider replay.
- It does not prove readiness, live provider availability, endpoint coverage, broker readiness, or write capability.
- It does not expose full probe payloads, endpoint response bodies, tokens, allowlist members, or fixture paths.

