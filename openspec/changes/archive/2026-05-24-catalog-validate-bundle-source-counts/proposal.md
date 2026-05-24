# Proposal: Catalog Validate Bundle Source Counts

## Why

E-11 catalog validation reports selected bundle step totals, but callers cannot see the step source distribution across all selected bundles without reading every resolved bundle. A compact `bundle_step_source_counts` aggregate makes the validation payload more self-describing while preserving the non-executing registry boundary.

## What Changes

- Add `bundle_step_source_counts` to `catalog validate` detailed validation payloads.
- Project `bundle_step_source_counts` through `catalog validate --view summary`.
- Derive counts only from already-resolved selected bundle steps.
- Preserve existing task/report-specific source counts, label counts, samples, and non-execution behavior.

## Out Of Scope

- No new catalog entries, bundle execution, workflow builder behavior, trade dispatch, task/report execution, or bundle/step listing.

## Success Criteria

- Detailed validation reports deterministic bundle step source counts.
- `sum(bundle_step_source_counts.values())` equals `bundle_step_count`.
- Summary view preserves the detailed `bundle_step_source_counts`.
