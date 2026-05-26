# Design: Provider replay primary error sample diagnostics

## Context

`_build_provider_replay_probe_summary()` already builds bounded `error_samples` and primary sample probe/status hints. Each sample may include compact diagnostic fields such as `error_code` and `http_status`, but those fields are still nested in the sample list.

## Goals / Non-Goals

- Goal: expose the first error sample error code as `primary_error_sample_error_code`.
- Goal: expose the first error sample HTTP status as `primary_error_sample_http_status`.
- Goal: return `None` when the first sample lacks a valid string error code or integer HTTP status.
- Non-goal: request additional probes.
- Non-goal: expose full probe payloads beyond the existing bounded error sample.
- Non-goal: start sockets, mutate providers, schedule retries/backoff, or manage daemon lifecycle.

## Decisions

- Derive both fields directly from `error_samples[0]` after sample construction.
- Preserve existing error sample order, limit, truncation flag, and count maps.
- Treat boolean `http_status` values as invalid because booleans are integers in Python but are not HTTP status codes.

## Risks / Trade-offs

- The fields are additive and should be ignored by older callers.
- The fields identify one representative error sample only; they do not prove endpoint coverage, provider readiness, or service health.

## Migration Plan

No migration is required. Existing fields remain unchanged.

## Open Questions

None.
