## Why

`governance.evaluation_summary` already exposes `stale_components` and `stale_count`, but compact consumers still need to inspect the list to identify the first stale dimension that drove manual-review posture. A single primary stale component gives operators and summary views a stable, bounded hint without exposing raw payloads or changing lifecycle behavior.

## What Changes

- Add additive `status_summary.governance.evaluation_summary.primary_stale_component`.
- Derive it from the existing `stale_components` ordering.
- Preserve existing component lists, counts, and advisory governance semantics.

## Impact

- No reconnect, backoff, restart, worker lifecycle, HTTP, SSE, or event-stream behavior changes.
- CLI and HTTP summary views keep projecting the existing compact `evaluation_summary`.
- Existing consumers remain compatible because the field is additive.

