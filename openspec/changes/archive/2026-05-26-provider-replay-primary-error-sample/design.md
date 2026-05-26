# Design: Provider replay primary error sample

## Context

`_build_provider_replay_probe_summary()` already derives bounded `error_samples` from existing probe results and exposes sample counts, status counts, probe counts, limits, and truncation. The first sample is already deterministic because probes are visited in `PROVIDER_REPLAY_STATUS_PROBE_KEYS` order.

## Goals / Non-Goals

- Goal: expose the first error sample probe as `primary_error_sample_probe`.
- Goal: expose the first error sample status as `primary_error_sample_status`.
- Goal: return `None` when `error_samples` is empty or the first sample lacks the relevant string field.
- Non-goal: request additional probes.
- Non-goal: expose full probe payloads beyond the existing bounded sample.
- Non-goal: start sockets, mutate providers, schedule retries/backoff, or manage daemon lifecycle.

## Decisions

- Derive both fields directly from `error_samples[0]` after sample construction.
- Keep existing error sample ordering, sample limit, truncation flag, and count maps unchanged.
- Do not add error-code primary fields in this slice; probe and status identity are sufficient for compact triage.

## Risks / Trade-offs

- The fields are additive and should be ignored by older callers.
- The fields identify a representative sample only; they do not prove overall replay service health.

## Migration Plan

No migration is required. Existing fields remain unchanged.

## Open Questions

None.
