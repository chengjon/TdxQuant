# Design: Provider replay error sample HTTP status counts

## Context

`runtime.probe_summary` currently has several HTTP status count maps:

- `requested_http_status_counts`: all requested probes with integer HTTP status values.
- `healthy_http_status_counts`: requested healthy probes with integer HTTP status values.
- `failed_http_status_counts`: requested non-healthy probes with integer HTTP status values.

The compact error sample candidate set is broader than failed probes because a healthy probe with an error code is still considered an error sample candidate. A dedicated error-sample HTTP status map makes that candidate set observable without exposing full probe payloads.

## Goals / Non-Goals

- Goal: expose `error_sample_http_status_counts` as string-keyed integer HTTP status counts for probes that enter the existing error sample candidate set.
- Goal: expose `error_sample_http_status_key_count` as the number of distinct keys in that map.
- Non-goal: change which probes enter `error_samples` or `error_sample_count`.
- Non-goal: expose full probe payloads, tokens, allowlist members, fixture paths, or endpoint internals.
- Non-goal: add start/stop lifecycle control, scheduling, restart/backoff, or provider mutation behavior.

## Decisions

- Count only integer, non-boolean `http_status` values on existing error sample candidates.
- Use string keys to match the existing HTTP status count maps.
- Keep the map independent of the bounded `error_samples` list so truncation does not hide distribution metadata.

## Risks / Trade-offs

- The field can be confused with `failed_http_status_counts`. The spec and `FUNCTION_TREE.md` boundary distinguish that this map covers the error sample candidate set, not only failed probes.

## Migration Plan

No migration required. Existing probe summary fields remain unchanged.

## Open Questions

None.
