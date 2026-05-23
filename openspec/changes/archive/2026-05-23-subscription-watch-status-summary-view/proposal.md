## Why

`bridge watch-status` currently prints the detailed worker response, which contains `status_summary.governance.action_summary` only when the caller knows where to look. Operators need a compact CLI view that surfaces the long-run status and governance rollup without scanning the full payload.

Adding a summary view keeps the detailed response unchanged while making the read-only governance posture easier to inspect.

## What Changes

- Add `--view detailed|summary` to `bridge watch-status`, defaulting to `detailed`.
- When `--view summary` is selected, print a compact payload derived from the existing watch status response.
- Include `status_summary.governance.action_summary` in the compact payload when available.
- Keep detailed output, bridge HTTP behavior, SSE/event-stream behavior, and lifecycle behavior unchanged.
- Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: expose a CLI summary view for bridge watch status that surfaces the existing governance action rollup.

## Impact

- CLI parser/handler: `tdxquant/cli.py`
- Tests: `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-subscription-long-run-status-summary/spec.md`
