# Design: Provider Replay Probe Has Hidden Error Sample

## Context

Provider replay probe summary already computes `error_sample_visible_count`, `error_sample_hidden_count`, `error_sample_truncated`, and bounded `error_samples`. CLI summary views copy `runtime.probe_summary` without executing commands or probing beyond the caller's requested flags.

## Design

Expose `runtime.probe_summary.has_hidden_error_sample` as `bool(error_sample_hidden_count)`. This gives compact consumers a stable limit/truncation presence flag while keeping `error_sample_hidden_count`, `error_sample_truncated`, and `error_sample_summary` authoritative for details.

Tests cover no-probe status, degraded status with no hidden sample, multi-probe status with hidden samples, and CLI summary projection.

## Non-Goals

- Do not add new probe endpoints or request unrequested probes.
- Do not change health/degraded classification, count maps, sample ordering, sample limit, or primary sample derivation.
- Do not start sockets, manage daemon lifecycle, restart/backoff, schedule probes, mutate providers, or enable write behavior.
- Do not claim broker readiness, provider readiness, endpoint coverage, or production daemon control.
