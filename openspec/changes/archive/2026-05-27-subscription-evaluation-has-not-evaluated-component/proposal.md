# Proposal: Subscription Evaluation Has Not-Evaluated Component

## Why

`status_summary.governance.evaluation_summary` lists not-evaluated components and counts them, but compact consumers still need to inspect arrays or counts to know whether any governance component remains outside stale/fresh evaluation. B-16/E-09 remains partial, so this should stay an advisory read-only summary hint.

## What Changes

- Add additive `status_summary.governance.evaluation_summary.has_not_evaluated_component`.
- Derive it from existing `not_evaluated_components`/`not_evaluated_count` output.
- Preserve existing advisory governance semantics and summary-view projection boundaries.

## Impact

- Affected spec: `tdx-subscription-long-run-status-summary`
- Affected code: subscription watch governance evaluation summary, HTTP/CLI summary projection tests, and `FUNCTION_TREE.md` B-16/E-09 registry evidence/boundary.
