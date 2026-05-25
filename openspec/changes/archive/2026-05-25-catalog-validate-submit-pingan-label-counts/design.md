## Context

Catalog validation already builds label counts for all selected bundles and task/report bundles. It also identifies submit-once and PingAn bundle subsets and exposes deterministic samples for both. The missing piece is a compact label distribution for those subsets.

## Goals / Non-Goals

- Add deterministic label-count objects for submit-once and PingAn bundle subsets.
- Include both fields in detailed validation output and opt-in summary view.
- Keep counts scoped to the selected resolved bundle set and current label filters.
- Do not execute catalog entries, reports, tasks, bundle steps, or trade commands.
- Do not infer runtime readiness, broker support, or trading safety from labels.

## Decisions

- Count labels from bundle-level `labels` arrays only.
- Reuse the existing submit-once and PingAn subset detection used for counts and samples.
- Sort label keys before returning to keep JSON stable.

## Risks / Trade-offs

- Labels are registry metadata, not proof of executable coverage. The field must be documented in `FUNCTION_TREE.md` as structure-only evidence.
- Submit-once and PingAn subsets can overlap; each subset gets its own independent label-count object.
