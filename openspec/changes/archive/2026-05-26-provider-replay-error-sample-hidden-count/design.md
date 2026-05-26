# Design: Provider replay hidden error sample count

## Context

`_build_provider_replay_probe_summary()` already tracks `error_sample_count` across all candidate error samples and returns a bounded `error_samples` list capped by `PROVIDER_REPLAY_PROBE_ERROR_SAMPLE_LIMIT`. `error_sample_truncated` currently exposes only a boolean.

## Goals / Non-Goals

- Goal: expose how many error sample candidates are not present in the bounded `error_samples` list.
- Goal: derive the value only from existing `error_sample_count` and `error_samples`.
- Non-goal: change the sample limit, sample ordering, or truncation condition.
- Non-goal: request additional probes or expose full probe payloads.
- Non-goal: start sockets, mutate providers, schedule retries/backoff, or manage daemon lifecycle.

## Decisions

- Compute `error_sample_hidden_count` as `max(error_sample_count - len(error_samples), 0)`.
- Place the field near `error_sample_limit` and `error_sample_truncated` in the summary payload.
- Keep the field numeric even when no samples exist; the value is `0`.

## Risks / Trade-offs

- The field is additive and should be ignored by older callers.
- The value measures sample truncation only; it does not prove provider readiness, endpoint coverage, or replay service health.

## Migration Plan

No migration is required. Existing fields remain unchanged.

## Open Questions

None.
