# Proposal: Catalog Validate Submit/PingAn Step Option-Key Counts

## Why

`catalog validate --view summary` exposes step option-key count maps for submit-once and PingAn bundle subsets. A compact distinct option-key count lets callers inspect option-key breadth without reading the map as a full option manifest or executable workflow.

## What Changes

- Add `submit_once_bundle_step_option_key_count` to the catalog validate summary view.
- Add `pingan_bundle_step_option_key_count` to the catalog validate summary view.
- Derive both fields from the number of keys in the already projected subset step option-key count maps.
- Update tests, OpenSpec, and `FUNCTION_TREE.md` evidence/boundary.

## Non-Goals

- Do not execute catalog entries, tasks, reports, trades, or bundle steps.
- Do not expose option values or validate option semantics.
- Do not change detailed validation payloads, option-key classification, or bundle resolution.
- Do not imply workflow-builder behavior, execution coverage, broker readiness, or trading safety.
