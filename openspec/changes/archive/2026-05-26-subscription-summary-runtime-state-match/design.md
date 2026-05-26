# Design: Subscription runtime state match

## Context

The detailed subscription watch status payload keeps raw `control` and `watch_status` dictionaries. Summary views intentionally expose only selected runtime identity fields plus status/governance rollups. Today they include `runtime.control_state` and `runtime.watch_state`, but not a direct comparison.

`runtime.state_match` is a compact consistency hint derived from fields already present in the summary view. It does not change controller state or decide whether recovery should happen.

## Goals / Non-Goals

- Goal: expose `runtime.state_match=true` when both states exist and match.
- Goal: expose `runtime.state_match=false` when both states exist and differ.
- Goal: omit `runtime.state_match` when either state is absent.
- Non-goal: trigger reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior.
- Non-goal: infer health, freshness, or readiness from state equality.

## Decisions

- Derive the hint in both HTTP and CLI runtime-view helpers after reading `control.state` and `watch_status.state`.
- Keep the field under `runtime` because it describes the runtime identity projection, not governance posture.
- Omit rather than return `null` for missing state inputs, preserving current sparse runtime projection behavior.

## Risks / Trade-offs

- State equality is only a narrow consistency hint. The registry and spec explicitly prevent treating it as health/readiness or lifecycle control.

## Migration Plan

No migration required. Existing summary fields remain unchanged.

## Open Questions

None.
