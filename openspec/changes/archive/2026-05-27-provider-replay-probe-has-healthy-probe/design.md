# Design: Provider Replay Probe Has Healthy Probe

## Context

Provider replay probe summary already computes `healthy_count`, ordered `healthy` probe names, `primary_healthy_probe`, and outcome booleans for failed/unhealthy probes. CLI summary views copy `runtime.probe_summary` without executing commands or probing beyond the caller's requested flags.

## Design

Expose `runtime.probe_summary.has_healthy_probe` as `bool(healthy)`. This gives compact consumers a stable healthy-presence flag while keeping `healthy_count`, `healthy`, and `primary_healthy_probe` authoritative for details.

Tests cover no-probe status, degraded status with no healthy probe, multi-probe status with healthy probes, and CLI summary projection.

## Non-Goals

- Do not add new probe endpoints or request unrequested probes.
- Do not change health/degraded classification, count maps, probe ordering, or primary probe derivation.
- Do not start sockets, manage daemon lifecycle, restart/backoff, schedule probes, mutate providers, or enable write behavior.
- Do not claim broker readiness, provider readiness, endpoint coverage, or production daemon control.
