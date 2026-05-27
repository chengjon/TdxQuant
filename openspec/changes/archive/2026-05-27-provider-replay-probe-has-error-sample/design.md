# Design: Provider Replay Probe Has Error Sample

## Context

Provider replay probe summary already computes `error_sample_count`, visible/hidden counts, bounded `error_samples`, and primary error-sample identity fields. CLI summary views copy `runtime.probe_summary` without executing commands or probing beyond the caller's requested flags.

## Design

Expose `runtime.probe_summary.has_error_sample` as `bool(error_sample_count)`. This gives compact consumers a stable presence flag while keeping `error_sample_count`, `error_sample_summary`, and `error_samples` authoritative for details.

Tests cover no-probe status, degraded status with one error sample, and CLI summary projection.

## Non-Goals

- Do not add new probe endpoints or request unrequested probes.
- Do not change health/degraded classification, count maps, sample ordering, sample limit, or primary sample derivation.
- Do not start sockets, manage daemon lifecycle, restart/backoff, schedule probes, mutate providers, or enable write behavior.
- Do not claim broker readiness, provider readiness, endpoint coverage, or production daemon control.
