# Proposal: Subscription Evaluation All Components Evaluated

## Why

`status_summary.governance.evaluation_summary` now exposes stale, fresh, and not-evaluated presence flags, but compact consumers still need to invert `has_not_evaluated_component` or inspect counts to know whether all governance components were evaluated. B-16/E-09 remains partial, so this must remain an advisory read-only summary hint.

## What Changes

- Add additive `status_summary.governance.evaluation_summary.all_components_evaluated`.
- Derive it from existing `not_evaluated_components`/`not_evaluated_count` output.
- Preserve existing advisory governance semantics and summary-view projection boundaries.

## Impact

- Affected spec: `tdx-subscription-long-run-status-summary`
- Affected code: subscription watch governance evaluation summary, HTTP/CLI summary projection tests, and `FUNCTION_TREE.md` B-16/E-09 registry evidence/boundary.
