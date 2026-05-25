## Design

`_validate_catalog_registry` already resolves selected catalog bundles and accumulates `task_report_bundle_step_option_key_counts` inside the task+report bundle branch. Extend that same branch to maintain a second map keyed as `source:option_key`.

The summary view should deep-copy the detailed validation field the same way it handles adjacent aggregate count maps. The field is additive and absent of option values, complete manifests, or execution output.

## Boundary

- Count only selected resolved bundles that contain both task and report steps.
- Count only string, non-empty option keys from object-valued `options`.
- Format keys as `<source>:<option_key>` using the resolved step `source`.
- Do not expose option values or full bundle step manifests.
- Do not execute catalog entries, tasks, reports, trades, or bundle steps.
