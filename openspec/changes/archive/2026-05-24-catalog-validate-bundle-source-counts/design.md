# Design: Catalog Validate Bundle Source Counts

## Approach

Extend `_validate_catalog_registry()` with a `bundle_step_source_counts` dictionary. During bundle validation, after a bundle passes optional label filtering and is counted as selected, increment the source of each resolved step. Sort keys before returning the validation payload.

`_build_catalog_summary_view()` explicitly projects validation fields, so add `bundle_step_source_counts` there with a deep copy.

## Compatibility

This is an additive validation field. Existing counts, samples, task/report-specific source counts, label counts, and errors keep their current semantics.

## Boundaries

`bundle_step_source_counts` is a read-only aggregate over selected resolved bundle steps. It is not a full bundle or step list, not execution evidence, and not proof that any task, report, trade, or bundle is available to run successfully.
