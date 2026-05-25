## Design

`_validate_catalog_registry` already identifies submit-once and PingAn bundle subsets while accumulating their label/source/name/source-name/entry counts. Extend those existing branches with option-key counters for object-valued step `options`.

The summary view should deep-copy both count maps from the detailed validation payload. Empty maps are meaningful: they state that the selected subset has no option keys without implying execution support or broker readiness.

## Boundary

- Count only selected resolved bundles in the submit-once or PingAn subset.
- Count only string, non-empty option keys from object-valued `options`.
- Do not expose option values or full bundle step manifests.
- Do not execute catalog entries, tasks, reports, trades, or bundle steps.
- Do not claim broker readiness, execution coverage, or trade safety.
