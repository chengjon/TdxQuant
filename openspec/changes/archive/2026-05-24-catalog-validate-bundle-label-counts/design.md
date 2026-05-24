# Design: Catalog Validate Bundle Label Counts

## Approach

Extend `_validate_catalog_registry()` with a `bundle_label_counts` dictionary. During bundle validation, after a bundle passes optional label filtering and is counted as selected, increment each non-empty resolved bundle label. Sort keys before returning the validation payload.

`_build_catalog_summary_view()` already projects selected validation fields explicitly, so add `bundle_label_counts` there with a deep copy.

## Compatibility

This is an additive validation field. Existing counts, samples, task/report-specific label counts, and errors keep their existing semantics.

## Boundaries

`bundle_label_counts` is a read-only aggregate over selected resolved bundles. It is not a full bundle list, not step detail, not execution evidence, and not proof that any task, report, trade, or bundle is available to run successfully.
