# Proposal: Catalog Validate Step Source Key Counts

## Why

`catalog validate --view summary` already exposes step source count maps for selected bundles and task/report bundle subsets. Callers that only need to know how many distinct source categories are represented must currently count map keys themselves.

## What Changes

- Add `bundle_step_source_key_count` to the catalog validate summary view.
- Add `task_report_bundle_step_source_key_count` to the catalog validate summary view.
- Derive both values from the number of keys in the already projected source-count maps.
- Update tests, OpenSpec, and `FUNCTION_TREE.md` evidence/boundary.

## Non-Goals

- Do not execute catalog entries, tasks, reports, trades, or bundle steps.
- Do not list full bundle/step manifests or option values.
- Do not change detailed validation payloads, source classification, or bundle resolution.
- Do not imply workflow-builder behavior, execution coverage, broker readiness, or trading safety.
