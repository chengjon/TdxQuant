## Why

B-16/E-09 currently expose advisory governance actions and a primary action rollup, but maintainers cannot see the severity distribution without reading the full `governance.actions` list. A compact severity count keeps summary evidence useful while preserving the no-automation boundary.

## What Changes

- Add `governance.action_summary.severity_counts` to subscription long-run status summaries.
- Derive the counts from existing advisory `governance.actions` entries.
- Preserve existing observe/manual-review decisions, reason generation, action generation, and lifecycle behavior.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: governance action summary includes advisory severity distribution counts.

## Impact

- Code: `tdxquant/subscription_watch_background.py`
- Tests: `tests/test_subscription_watch_background.py`
- Specs: `openspec/specs/tdx-subscription-long-run-status-summary/spec.md`
- Registry: `FUNCTION_TREE.md` remains the single feature/status registry.
