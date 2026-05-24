# Design: Catalog Validate Task Report Step Count

## Derivation

During `_validate_catalog_registry()`, when a resolved bundle contains both task and report sources, increment `task_report_bundle_step_count` by the number of resolved steps in that bundle.

This count is the total step footprint across matching task/report bundles after applying the existing kind, bundle, and label filters.

## Projection

`_build_catalog_summary_view()` will copy the scalar into the reduced summary view next to `task_report_bundle_count`, samples, source counts, and label counts.

## Boundary

The field is a derived validation count. It does not execute entries or prove any task/report/trade workflow is runnable.

## Testing

Add focused tests for detailed validation, summary view projection, and filtered no-match behavior.
