# Design: Catalog Validate Bundle Step Count

## Approach

Increment a `bundle_step_count` scalar whenever a resolved bundle is counted during `_validate_catalog_registry()`. Copy the scalar into the summary view the same way as the existing bundle and task/report counters.

## Compatibility

The new field is additive. Existing bundle validation, task/report counters, samples, label counts, and non-execution metadata remain unchanged.

## Boundaries

`bundle_step_count` is a validation-time scalar only. It does not execute catalog steps, does not expand into a workflow builder, and does not imply that any bundle step is runnable in the current environment.
