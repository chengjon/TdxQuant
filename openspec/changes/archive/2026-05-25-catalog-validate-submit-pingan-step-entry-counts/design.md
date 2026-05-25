## Context

Catalog validation already computes step-entry counts for all selected bundles and task/report bundle subsets. Submit-once and PingAn subsets now have count, label, sample, step-source, step-name, and source-name fields, but not the resolved entry distribution.

## Goals / Non-Goals

- Add deterministic step-entry count objects for submit-once and PingAn bundle subsets.
- Include both fields in detailed validation output and opt-in summary view.
- Keep counts scoped to the selected resolved bundle set and current label filters.
- Do not execute catalog entries, reports, tasks, bundle steps, or trade commands.
- Do not expose full bundle details or infer workflow completeness, runtime readiness, broker support, execution ordering guarantees, or trading safety from entry names.

## Decisions

- Count resolved bundle step `entry` values only when they are non-empty strings.
- Reuse the existing submit-once and PingAn subset detection used for counts, labels, samples, step-source counts, step-name counts, and source-name counts.
- Sort entry keys before returning to keep JSON stable.

## Risks / Trade-offs

- Entry counts are more specific than source/name counts and may look close to an execution manifest. The field remains an aggregate only and must not replace full bundle inspection or execution audit evidence.
