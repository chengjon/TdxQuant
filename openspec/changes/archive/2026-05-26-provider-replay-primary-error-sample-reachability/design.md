# Design: Provider replay primary error sample reachability

## Context

`runtime.probe_summary` includes bounded error samples and primary fields for the first compact error sample: probe, status, error code, and HTTP status. The new `error_sample_reachability_counts` map summarizes the whole candidate set, but callers still need a compact first-sample hint for reachability.

## Goals / Non-Goals

- Goal: expose `primary_error_sample_reachability` for the first error sample candidate.
- Goal: reuse the same reachability bucket semantics as other probe summary maps.
- Non-goal: change `error_samples` payload shape or ordering.
- Non-goal: expose full probe payloads, tokens, allowlist members, fixture paths, or endpoint internals.
- Non-goal: add start/stop lifecycle control, scheduling, restart/backoff, or provider mutation behavior.

## Decisions

- Capture the first error sample candidate's reachability bucket while building the candidate set.
- Use `null` when no error sample candidate exists.
- Use `unknown` when the first candidate has missing or non-boolean reachability.

## Risks / Trade-offs

- The field is advisory and can be confused with a service health verdict. `FUNCTION_TREE.md` and the spec boundary identify it as first-candidate diagnostic metadata only.

## Migration Plan

No migration required. Existing probe summary fields remain unchanged.

## Open Questions

None.
