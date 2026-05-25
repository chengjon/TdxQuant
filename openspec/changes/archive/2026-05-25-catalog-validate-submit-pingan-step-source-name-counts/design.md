## Context

Catalog validation already computes `source:name` counts for all selected bundles and task/report bundle subsets. Submit-once and PingAn subsets now have count, label, sample, step-source, and step-name fields, but not the combined source-name distribution.

## Goals / Non-Goals

- Add deterministic source-name count objects for submit-once and PingAn bundle subsets.
- Include both fields in detailed validation output and opt-in summary view.
- Keep counts scoped to the selected resolved bundle set and current label filters.
- Do not execute catalog entries, reports, tasks, bundle steps, or trade commands.
- Do not infer workflow completeness, runtime readiness, broker support, execution ordering guarantees, or trading safety from source-name pairs.

## Decisions

- Count resolved bundle step pairs as `<source>:<name>` only when both values are non-empty strings.
- Reuse the existing submit-once and PingAn subset detection used for counts, labels, samples, step-source counts, and step-name counts.
- Sort source-name keys before returning to keep JSON stable.

## Risks / Trade-offs

- The field overlaps with global bundle source-name counts when callers filter by a subset label. Keeping explicit subset fields still helps summary consumers avoid reconstructing subset composition from full detail rows.
