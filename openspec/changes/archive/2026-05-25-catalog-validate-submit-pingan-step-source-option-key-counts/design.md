## Design

Extend the existing submit-once and PingAn option-key counters in `_validate_catalog_registry` with source-qualified maps keyed as `<source>:<option_key>`. These maps should be updated only when a resolved step has a string source and an object-valued `options` map.

The summary view should deep-copy both detailed validation maps. Empty maps are preserved as explicit evidence that the selected subset has no source-qualified option keys.

## Boundary

- Count only selected resolved bundles in the submit-once or PingAn subset.
- Count only string, non-empty option keys from object-valued `options`.
- Include source only when the resolved step has a string, non-empty `source`.
- Do not expose option values or full bundle step manifests.
- Do not execute catalog entries, tasks, reports, trades, or bundle steps.
- Do not claim broker readiness, execution coverage, or trade safety.
