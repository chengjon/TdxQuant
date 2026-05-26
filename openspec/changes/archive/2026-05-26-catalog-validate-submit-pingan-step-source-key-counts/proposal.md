# Proposal: Catalog Validate Submit/PingAn Step Source Key Counts

## Why

`catalog validate --view summary` exposes step source count maps for submit-once and PingAn bundle subsets. A compact distinct-source count helps readers see how many source categories are represented without treating the count map as a full step manifest.

## What Changes

- Add `submit_once_bundle_step_source_key_count` to the catalog validate summary view.
- Add `pingan_bundle_step_source_key_count` to the catalog validate summary view.
- Derive both fields from the number of keys in the already projected subset step source-count maps.
- Update tests, OpenSpec, and `FUNCTION_TREE.md` evidence/boundary.

## Non-Goals

- Do not execute catalog entries, tasks, reports, trades, or bundle steps.
- Do not list full bundle manifests, full step manifests, or option values.
- Do not change detailed validation payloads, source classification, or bundle resolution.
- Do not imply workflow-builder behavior, execution coverage, broker readiness, or trading safety.
