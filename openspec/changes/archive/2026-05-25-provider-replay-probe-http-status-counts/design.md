## Context

`_build_provider_replay_probe_summary()` already derives requested-only status and reachability maps from normalized probe objects. Requested probes also carry `http_status` when a response was observed. The new field can be computed in the same fixed-probe loop.

## Goals / Non-Goals

- Goal: expose `runtime.probe_summary.requested_http_status_counts` for requested probes.
- Goal: omit probes with no integer HTTP status instead of inventing a synthetic code.
- Non-goal: adding new probe targets, changing probe execution, starting sockets, managing daemon lifecycle, or treating HTTP status counts as health/readiness automation.

## Decisions

- Count only integer `http_status` values. Missing/None/non-integer values are already represented by status, reachability, and error fields.
- Stringify numeric status codes in the returned map so JSON consumers get deterministic object keys.
- Sort the returned map by numeric code represented as a string, matching existing deterministic count-map style.

## Risks / Trade-offs

- HTTP status counts can overlap with reachability counts. Mitigation: document this as HTTP response metadata, not a replacement status model.
- Missing HTTP status values are not counted. Mitigation: those cases remain visible through reachability and error-code summaries.

## Migration Plan

The field is additive. Existing callers can ignore it. Rollback removes the field and related tests/spec delta.

## Open Questions

None.
