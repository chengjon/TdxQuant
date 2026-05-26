# Proposal: Catalog Validate Bundle Label Key Counts

## Why

`catalog validate --view summary` exposes bundle label count maps, but callers that only need distinct label-category counts must count map keys themselves. Adding explicit key counts keeps the summary self-contained while preserving the existing non-executing boundary.

## What Changes

- Add `bundle_label_key_count` to the catalog validate summary view.
- Add `task_report_bundle_label_key_count` to the catalog validate summary view.
- Derive both fields from the number of keys in the already projected label-count maps.
- Update tests, OpenSpec, and `FUNCTION_TREE.md` evidence/boundary.

## Non-Goals

- Do not execute catalog entries, tasks, reports, trades, or bundle steps.
- Do not list full bundle manifests or full label assignments.
- Do not change detailed validation payloads, label classification, or bundle resolution.
- Do not imply workflow-builder behavior, execution coverage, broker readiness, or trading safety.
