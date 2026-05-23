## Why

Detailed subscription watch status already includes `status_summary.governance.reasons`, while compact HTTP/CLI summary views intentionally omit the full reason list. That protects the reduced view boundary, but it also hides whether a manual-review posture came from one reason or several.

B-16 and E-09 are tracked as partial long-run governance work in `FUNCTION_TREE.md`. The compact view should expose enough bounded evidence for operators to understand advisory breadth without treating the summary as the full detailed payload.

## What Changes

- Add a derived `governance.reason_count` to bridge HTTP `watch/status?view=summary` when the underlying detailed governance payload provides a reasons list.
- Add the same derived field to CLI `bridge watch-status --view summary`.
- Continue omitting full `governance.reasons` and `governance.actions` from compact summary views.

## Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: compact subscription summary views expose a bounded governance reason count.

## Impact

- Code: `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`
- Docs/registry: `FUNCTION_TREE.md`
