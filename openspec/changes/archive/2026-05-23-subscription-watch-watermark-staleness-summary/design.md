## Context

`status_summary.heartbeat` already has explicit staleness semantics. Without a threshold, it remains `not_evaluated`; with a threshold, the summary reports fresh/stale plus evaluation metadata. `status_summary.watermark` currently carries `last_event_ts`, `last_sequence`, symbol counts, and source timestamp, but no staleness state.

Watermark staleness should follow the same additive, read-only pattern as heartbeat staleness. It should help diagnose event-flow freshness without becoming a scheduler, restart policy, or reconnect trigger.

## Goals / Non-Goals

**Goals:**

- Add explicit `watermark_stale_after_seconds` evaluation to status summary.
- Keep default watermark behavior additive and non-breaking.
- Forward the threshold through HTTP, registry, and CLI watch-status surfaces.

**Non-Goals:**

- No automatic wall-clock staleness inference by default.
- No reconnect/backoff/restart behavior changes.
- No change to watch events, SSE/event-stream, or run artifact formats.

## Decisions

- Use `last_event_ts` as the staleness timestamp, falling back to `last_event_at` through the existing summary field.
  - Rationale: this is already the public watermark timestamp in the status summary.
- Treat missing timestamps as `missing`, invalid thresholds as `invalid_threshold`, and parse failures as `invalid_timestamp`.
  - Rationale: the summary remains diagnostic rather than hiding malformed input.
- Add CLI flag `--watermark-stale-after-seconds`.
  - Rationale: it mirrors `--heartbeat-stale-after-seconds` and keeps the feature discoverable.

## Risks / Trade-offs

- Users may expect stale watermark to restart the watcher -> mitigate through boundary text and spec non-goals.
- A stale watermark with a fresh heartbeat is possible -> this is useful diagnostic information and should remain visible.
