## Why

B-16/E-09 already expose advisory subscription governance actions and severity distribution counts, but maintainers still need to inspect the full action list to see which advisory action types are present. A compact action-name count keeps the summary useful while preserving the no-automation boundary.

## What Changes

- Add `governance.action_summary.action_name_counts` to subscription long-run status summaries.
- Derive the counts from existing advisory `governance.actions` entries.
- Preserve existing observe/manual-review decisions, reason generation, action generation, summary-view hiding of full action lists, and lifecycle behavior.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: governance action summary includes advisory action-name distribution counts.

## Impact

- Code: `tdxquant/subscription_watch_background.py`.
- Tests: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`, `tests/test_api_cli.py`.
- Registry/specs: `FUNCTION_TREE.md`, `openspec/specs/tdx-subscription-long-run-status-summary/spec.md`.
