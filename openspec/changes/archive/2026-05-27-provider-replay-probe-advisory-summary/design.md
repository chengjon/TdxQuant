# provider replay probe advisory summary design

## Context

E-06 remains `[部分实现]`: provider replay is a foreground, replay-only fake provider with read-only status/config/probe inspection. Recent work made individual rollup fields precise, but that creates a high-cardinality surface for a caller that only needs one compact advisory object.

## Design

Extend `_build_provider_replay_probe_summary()` with an additive `advisory_summary` object after the existing request, health, and outcome summaries have been derived.

The object will mirror existing in-memory rollup values:

- `status`
- `request_coverage_status`
- `total_count`
- `requested_count`
- `healthy_count`
- `failed_count`
- `unhealthy_count`
- `has_requested_probe`
- `has_healthy_probe`
- `has_failed_probe`
- `has_unhealthy_probe`
- `has_problem_probe`
- `primary_problem_probe`
- `primary_error_sample_probe`
- `boundary`

The `boundary` value is a static marker such as `read_only_probe_summary` so downstream consumers can distinguish the object from readiness, lifecycle, or execution instructions.

The CLI summary view already copies the detailed `probe_summary`, so no CLI execution or projection change is required beyond tests that assert the new object is visible.

## Boundaries

- This change is read-only status metadata.
- It does not execute extra probes or make unrequested endpoints observable.
- It does not start, stop, restart, daemonize, schedule, supervise, or back off provider replay.
- It does not prove service readiness, live provider availability, endpoint coverage, broker readiness, workflow readiness, or write capability.
- It does not expose full probe payloads, endpoint response bodies, tokens, allowlist members, or fixture paths.

