## Design

`_validate_catalog_registry` already walks selected resolved bundle steps for the submit-once and PingAn subsets. Increment a dedicated step count in each existing subset branch, using the same resolved step iteration that feeds the source/name/source-name/entry/option-key maps.

The summary view should deep-copy the detailed scalar count. The count is an aggregate convenience field, not an execution signal.

## Boundary

- Count only selected resolved bundles in the submit-once or PingAn subset.
- Count resolved bundle steps, not catalog entries or executed operations.
- Do not expose full bundle step manifests.
- Do not execute catalog entries, tasks, reports, trades, or bundle steps.
- Do not claim broker readiness, execution coverage, workflow readiness, or trade safety.
