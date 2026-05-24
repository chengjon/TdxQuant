# Proposal: Catalog Validate Bundle Label Counts

## Why

E-11 catalog validation already reports selected bundle counts and task/report label counts, but callers cannot see the label distribution across all selected bundles without reading the full bundle registry. A compact `bundle_label_counts` aggregate keeps validation useful while preserving the non-executing registry boundary.

## What Changes

- Add `bundle_label_counts` to `catalog validate` detailed validation payloads.
- Project `bundle_label_counts` through `catalog validate --view summary`.
- Derive counts only from already-resolved selected bundles.
- Preserve existing sample limits, task/report-specific label counts, and non-execution behavior.

## Out Of Scope

- No new catalog entries, bundle execution, workflow builder behavior, trade dispatch, task/report execution, or bundle/step listing.

## Success Criteria

- Detailed validation reports deterministic bundle label counts.
- Summary view preserves the detailed `bundle_label_counts`.
- The field remains absent from execution payloads and does not expose full bundle definitions.
