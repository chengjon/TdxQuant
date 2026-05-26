# Design: Provider replay error sample reachability counts

## Context

`runtime.probe_summary` currently has reachability count maps for requested, healthy-only, and failed-only probe sets. The compact error sample candidate set is a separate diagnostic set: it includes non-healthy probes and healthy probes that still report an error code.

A dedicated error-sample reachability map makes that candidate set observable without exposing full probe payloads or changing which probes are sampled.

## Goals / Non-Goals

- Goal: expose `error_sample_reachability_counts` for existing error sample candidates.
- Goal: expose `error_sample_reachability_key_count` as the number of distinct reachability buckets.
- Non-goal: change which probes enter `error_samples` or `error_sample_count`.
- Non-goal: expose full probe payloads, tokens, allowlist members, fixture paths, or endpoint internals.
- Non-goal: add start/stop lifecycle control, scheduling, restart/backoff, or provider mutation behavior.

## Decisions

- Reuse the existing reachability bucket semantics: `reachable`, `unreachable`, and `unknown`.
- Count the full error sample candidate set, not only the bounded `error_samples` list, so truncation does not hide distribution metadata.
- Keep output keys sorted for stable CLI payloads.

## Risks / Trade-offs

- The field can be confused with `failed_reachability_counts`. The spec and `FUNCTION_TREE.md` boundary distinguish that this map covers the error sample candidate set, including healthy probes with error codes.

## Migration Plan

No migration required. Existing probe summary fields remain unchanged.

## Open Questions

None.
