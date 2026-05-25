## Context

`_build_provider_replay_probe_summary()` already iterates through the fixed provider replay probe keys and derives status count maps and target lists from normalized probe objects. Each normalized probe carries a `reachable` value that is `True`, `False`, or `None` for not-requested/unknown reachability.

## Goals / Non-Goals

- Goal: expose `runtime.probe_summary.requested_reachability_counts` for requested probes.
- Goal: use deterministic bucket names so CLI/JSON consumers do not depend on boolean object keys.
- Non-goal: adding new probe targets, changing probe execution, starting sockets, managing daemon lifecycle, or treating reachability counts as health/readiness automation.

## Decisions

- Exclude `not_requested` probes. The field name and existing `requested_status_counts` pattern make requested-only semantics explicit.
- Bucket `reachable=True` as `reachable`, `reachable=False` as `unreachable`, and any other value as `unknown`.
- Return sorted count maps for deterministic output, matching existing probe summary count fields.

## Risks / Trade-offs

- Reachability counts can overlap with status counts. Mitigation: document this as transport reachability metadata, not a replacement status model.
- Unknown reachability may be rare. Mitigation: preserving an `unknown` bucket keeps future probe adapters additive and deterministic.

## Migration Plan

The field is additive. Existing callers that ignore unknown keys continue working. Rollback removes the field and related tests/spec delta.

## Open Questions

None.
