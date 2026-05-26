# Proposal: Catalog Validate Submit/PingAn Label Key Counts

## Why

`catalog validate --view summary` already exposes label count maps for submit-once and PingAn bundle subsets. Callers that only need the number of distinct labels represented in those subsets currently have to count map keys themselves.

## What Changes

- Add `submit_once_bundle_label_key_count` to the catalog validate summary view.
- Add `pingan_bundle_label_key_count` to the catalog validate summary view.
- Derive both fields from the number of keys in the already projected subset label-count maps.
- Update tests, OpenSpec, and `FUNCTION_TREE.md` evidence/boundary.

## Non-Goals

- Do not execute catalog entries, tasks, reports, trades, or bundle steps.
- Do not list full bundle manifests or full label assignments.
- Do not change detailed validation payloads, label classification, or bundle resolution.
- Do not imply workflow-builder behavior, execution coverage, broker readiness, or trading safety.
