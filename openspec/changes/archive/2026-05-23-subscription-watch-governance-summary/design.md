## Context

`build_subscription_watch_status_summary()` already builds a stable additive projection with `heartbeat`, `watermark`, and `reconnect` sub-objects. Explicit heartbeat/watermark stale thresholds are opt-in, and the existing boundary says those diagnostics do not change reconnect or backoff behavior.

The next safe step for long-run governance is not automation. It is a compact advisory field that lets bridge, CLI, and scripts consume the status posture without reimplementing the same inference.

## Goals / Non-Goals

**Goals:**

- Add a deterministic `status_summary.governance` object.
- Keep it advisory-only and derived from existing summary data.
- Avoid wall-clock staleness inference unless stale thresholds were explicitly provided.
- Cover active observe, reconnect/degraded manual review, and explicit stale diagnostics in tests.

**Non-Goals:**

- No automatic reconnect, restart, process supervision, or backoff scheduling.
- No change to controller start/stop/list/events/logs.
- No change to bridge HTTP/SSE event-stream contracts.

## Decisions

- Use `decision` values `observe` and `manual_review`.
  - Rationale: the field stays stable and conservative; automation can still inspect structured `reasons` later without introducing action semantics now.
- Include `reasons` as strings such as `overall_status:reconnecting` and `heartbeat:stale`.
  - Rationale: callers can display or filter without parsing nested status objects.
- Include `staleness_evaluated`.
  - Rationale: this makes the "no default wall-clock stale inference" boundary visible in the same sub-object.
- Include an explicit `boundary` string.
  - Rationale: this mirrors existing registry language and prevents consumers from treating advisory output as a scheduler.

## Risks / Trade-offs

- Callers may overinterpret `manual_review`.
  - Mitigation: the field uses advisory names and embeds an advisory-only boundary string.
- Additional summary keys can affect strict consumers.
  - Mitigation: existing summary behavior is additive, and current bridge/CLI paths preserve summary payloads rather than enforcing exact schemas.
