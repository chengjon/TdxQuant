## Context

Catalog validation already computes step-name counts for all selected bundles and task/report bundle subsets. Submit-once and PingAn subsets have counts, labels, samples, and step-source distributions, but not their resolved step-name distribution.

## Goals / Non-Goals

- Add deterministic step-name count objects for submit-once and PingAn bundle subsets.
- Include both fields in detailed validation output and opt-in summary view.
- Keep counts scoped to the selected resolved bundle set and current label filters.
- Do not execute catalog entries, reports, tasks, bundle steps, or trade commands.
- Do not infer workflow completeness, runtime readiness, broker support, execution ordering guarantees, or trading safety from step names.

## Decisions

- Count resolved bundle step `name` values only.
- Reuse the existing submit-once and PingAn subset detection used for counts, labels, samples, and step-source counts.
- Sort step-name keys before returning to keep JSON stable.

## Risks / Trade-offs

- The field overlaps with global bundle step-name counts when callers filter by a subset label. Keeping explicit subset fields still helps summary consumers avoid inferring subset composition from filters.
