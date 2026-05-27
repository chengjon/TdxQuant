# Proposal: Subscription Evaluation Has Fresh Component

## Why

`status_summary.governance.evaluation_summary` now exposes stale and not-evaluated presence flags, but compact consumers still need to inspect `fresh_components` or `fresh_count` to know whether any evaluated component is fresh. B-16/E-09 remains partial, so this should stay an advisory read-only summary hint rather than lifecycle automation.

## What Changes

- Add additive `status_summary.governance.evaluation_summary.has_fresh_component`.
- Derive it from existing `fresh_components`/`fresh_count` output.
- Preserve existing advisory governance semantics and summary-view projection boundaries.

## Impact

- Affected spec: `tdx-subscription-long-run-status-summary`
- Affected code: subscription watch governance evaluation summary, HTTP/CLI summary projection tests, and `FUNCTION_TREE.md` B-16/E-09 registry evidence/boundary.
