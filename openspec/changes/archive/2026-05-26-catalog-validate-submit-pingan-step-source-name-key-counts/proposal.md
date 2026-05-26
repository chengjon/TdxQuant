# Proposal: Catalog Validate Submit/PingAn Step Source-Name Key Counts

## Why

`catalog validate --view summary` exposes step `source:name` count maps for submit-once and PingAn bundle subsets. A compact distinct `source:name` key count helps readers understand the breadth of resolved step categories without treating the map as a full manifest or execution plan.

## What Changes

- Add `submit_once_bundle_step_source_name_key_count` to the catalog validate summary view.
- Add `pingan_bundle_step_source_name_key_count` to the catalog validate summary view.
- Derive both fields from the number of keys in the already projected subset step `source:name` count maps.
- Update tests, OpenSpec, and `FUNCTION_TREE.md` evidence/boundary.

## Non-Goals

- Do not execute catalog entries, tasks, reports, trades, or bundle steps.
- Do not list full bundle manifests, full step manifests, or option values.
- Do not change detailed validation payloads, source/name classification, or bundle resolution.
- Do not imply workflow-builder behavior, execution coverage, broker readiness, or trading safety.
