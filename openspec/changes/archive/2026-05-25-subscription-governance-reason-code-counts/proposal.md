## Why

B-16/E-09 already exposes advisory governance reasons, source-prefix counts, and bounded reason samples for subscription long-run status. Maintainers can see which component family contributed a reason, but not a compact distribution of the exact advisory reason codes without reading the full `governance.reasons` list.

Adding reason-code counts keeps the registry evidence precise for long-run diagnostics while preserving the existing advisory-only boundary.

## What Changes

- Add `governance.reason_summary.reason_code_counts` to subscription long-run status summaries.
- Derive the counts from existing advisory `governance.reasons` entries.
- Preserve existing observe/manual-review decisions, reason generation, action generation, reconnect/backoff behavior, and lifecycle behavior.
- Preserve compact bridge/CLI summary behavior by carrying the field inside the existing `reason_summary` projection without exposing raw `reasons` or `actions`.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: governance reason summary includes exact advisory reason-code distribution counts.
- `tdx-worker-bridge-http-control-plane`: watch-status summary keeps projecting compact `governance.reason_summary`, including the new reason-code counts when supplied.

## Impact

- Code: `tdxquant/subscription_watch_background.py`
- Tests: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`, `tests/test_api_cli.py`
- Specs: `openspec/specs/tdx-subscription-long-run-status-summary/spec.md`, `openspec/specs/tdx-worker-bridge-http-control-plane/spec.md`
- Registry: `FUNCTION_TREE.md` remains the single feature/status registry.

