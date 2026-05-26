# Design: Provider replay visible error sample count

## Context

`_build_provider_replay_probe_summary()` returns a bounded `error_samples` list and now exposes total and hidden candidate counts. A visible count completes the compact sample accounting tuple: total, visible, hidden, limit, and truncated.

## Goals / Non-Goals

- Goal: expose how many bounded error samples are present in the response.
- Goal: derive the value only from the existing `error_samples` list.
- Non-goal: change the sample limit, sample ordering, hidden count, or truncation condition.
- Non-goal: request additional probes or expose full probe payloads.
- Non-goal: start sockets, mutate providers, schedule retries/backoff, or manage daemon lifecycle.

## Decisions

- Compute `error_sample_visible_count` as `len(error_samples)`.
- Place the field near `error_sample_count`, `error_sample_hidden_count`, `error_sample_limit`, and `error_sample_truncated`.
- Keep the field numeric even when no samples exist; the value is `0`.

## Risks / Trade-offs

- The field is additive and should be ignored by older callers.
- The value measures bounded projection size only; it does not prove provider readiness, endpoint coverage, or replay service health.

## Migration Plan

No migration is required. Existing fields remain unchanged.

## Open Questions

None.
