# command-catalog-plan-step-source-summary-view

## Why

`FUNCTION_TREE.md` E-11 tracks many catalog bundles that compose task and report steps, while D-07/D-08 rely on catalog planning to expose PingAn trade-oriented wrappers without implying execution. The current plan/preview summary includes selected steps, provenance, and non-execution constraints, but it does not provide a compact machine-readable count of which command sources the selected plan would traverse.

This change adds source counts to the plan/preview summary view so readers can distinguish task/report/trade composition at a glance while preserving non-executing semantics.

## What Changes

- Add `step_source_counts` to bundle `catalog plan` and `catalog preview` summary views.
- Derive counts from the already resolved selected plan steps.
- Add focused CLI tests covering task/report bundle composition and selected-step filtering.
- Update `FUNCTION_TREE.md` E-11 evidence/boundary to document the new summary metadata.

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`

## Impact

- Runtime behavior: no change to `catalog run` execution semantics.
- Safety: plan and preview remain non-executing and keep provenance/constraint metadata.
- Registry: `FUNCTION_TREE.md` remains the single feature/status registry; no separate roadmap is introduced.
