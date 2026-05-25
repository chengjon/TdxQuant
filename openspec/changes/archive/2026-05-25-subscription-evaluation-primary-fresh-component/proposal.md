## Why

`governance.evaluation_summary` already exposes `fresh_components` and `fresh_count`, but compact consumers still need to inspect the list to identify the first explicitly fresh dimension. A single primary fresh component completes the compact primary component hints alongside stale and not-evaluated summaries.

## What Changes

- Add additive `status_summary.governance.evaluation_summary.primary_fresh_component`.
- Derive it from the existing `fresh_components` ordering.
- Preserve existing component lists, counts, primary stale/not-evaluated components, and advisory governance semantics.

## Impact

- No reconnect, backoff, restart, worker lifecycle, HTTP, SSE, or event-stream behavior changes.
- CLI and HTTP summary views keep projecting the existing compact `evaluation_summary`.
- Existing consumers remain compatible because the field is additive.

