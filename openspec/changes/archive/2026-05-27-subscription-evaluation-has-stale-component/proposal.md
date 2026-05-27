# Proposal: Subscription Evaluation Has Stale Component

## Why

`status_summary.governance.evaluation_summary` already exposes stale component lists and counts, but compact consumers still need to compare counts or inspect arrays to answer whether any governance component is stale. B-16/E-09 remains partial, so this should stay an advisory summary hint rather than lifecycle automation.

## What Changes

- Add additive `status_summary.governance.evaluation_summary.has_stale_component`.
- Derive it from existing `stale_components`/`stale_count` output.
- Preserve existing advisory governance semantics and summary-view projection boundaries.

## Impact

- Affected spec: `tdx-subscription-long-run-status-summary`
- Affected code: subscription watch governance evaluation summary, HTTP/CLI summary projection tests, and `FUNCTION_TREE.md` B-16/E-09 registry evidence/boundary.
