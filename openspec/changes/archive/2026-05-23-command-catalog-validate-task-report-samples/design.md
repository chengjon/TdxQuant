## Context

Command catalog bundles are fixed runtime JSON definitions. Validation already
proves that selected entries and bundles resolve without executing any steps,
and it counts task+report bundles for E-11. The missing piece is a compact,
deterministic sample list for summary-mode callers.

## Goals / Non-Goals

- Add a deterministic `task_report_bundle_samples` list to validation output.
- Derive samples only from bundles that have both `task` and `report` steps after successful resolution.
- Keep the sample list bounded and non-executing.
- Do not add arbitrary workflow building, execute catalog steps, or change list/plan/run summary views.

## Decisions

- Store up to five sample bundle ids.
  - Rationale: this is enough evidence for registry readers while keeping summary output compact.
  - Alternative considered: include every matching id. That would make the summary grow with the catalog and duplicate detailed JSON discovery.
- Add the sample list to both detailed validation and `summary_view`.
  - Rationale: detailed callers and summary callers should agree on the same validation evidence.
- Keep sample order deterministic by using the existing sorted bundle iteration.
  - Rationale: stable output avoids fixture churn.

## Risks / Trade-offs

- A bounded sample list can omit many valid bundles. Mitigation: keep the count field as the source of total coverage and name the field as samples.
- The catalog summary helper is shared by several catalog paths. Mitigation: only touch the validate branch and keep existing list/plan/run fields unchanged.

## Migration Plan

No migration is required. The new fields are additive and only present for validation results.

## Open Questions

None.
