# Design: Subscription runtime run-id match

## Context

The summary runtime view is intentionally a compact projection of raw `control` and `watch_status` state. It now includes the selected `run_id` and the source that supplied that value, while keeping the detailed payload as the only place where callers can inspect both raw run ids.

`runtime.run_id_match` adds a narrow consistency hint when both raw run ids are available. It does not decide ownership, freshness, health, or readiness.

## Goals / Non-Goals

- Goal: expose `runtime.run_id_match=true` when both raw run ids exist and match.
- Goal: expose `runtime.run_id_match=false` when both raw run ids exist and differ.
- Goal: omit `runtime.run_id_match` when either raw run id is absent.
- Non-goal: change the existing `runtime.run_id` source precedence.
- Non-goal: infer ownership, health, freshness, readiness, or lifecycle state from equality.
- Non-goal: trigger reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior.

## Decisions

- Derive the hint in both HTTP and CLI runtime-view helpers near the existing run-id projection.
- Keep the field under `runtime` because it describes runtime identity consistency, not governance posture.
- Preserve the existing sparse summary style by omitting the field when either input is absent.

## Risks / Trade-offs

- Run-id equality is only a narrow identity hint. The registry and spec explicitly prevent treating it as ownership, readiness, or lifecycle control.

## Migration Plan

No migration required. Existing summary fields remain unchanged.

## Open Questions

None.
