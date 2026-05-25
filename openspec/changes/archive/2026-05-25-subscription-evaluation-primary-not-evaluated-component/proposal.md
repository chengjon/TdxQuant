## Why

`governance.evaluation_summary` already exposes `not_evaluated_components` and `not_evaluated_count`, but compact consumers still need to inspect the list to identify the first missing evaluation dimension. A single primary not-evaluated component gives summary consumers a stable, bounded hint without exposing raw payloads or changing lifecycle behavior.

## What Changes

- Add additive `status_summary.governance.evaluation_summary.primary_not_evaluated_component`.
- Derive it from the existing `not_evaluated_components` ordering.
- Preserve existing component lists, counts, primary stale component, and advisory governance semantics.

## Impact

- No reconnect, backoff, restart, worker lifecycle, HTTP, SSE, or event-stream behavior changes.
- CLI and HTTP summary views keep projecting the existing compact `evaluation_summary`.
- Existing consumers remain compatible because the field is additive.

