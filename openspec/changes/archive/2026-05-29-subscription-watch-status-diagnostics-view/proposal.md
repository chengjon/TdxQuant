# Change: Add diagnostics view to subscription watch status

## Why

The subscription watch status path now exposes several read-only rollups (`control_rollup`, `consistency_rollup`, `reconnect_rollup`, `evaluation_rollup`), but operators still need a compact way to see the combined diagnostic posture without inspecting each rollup separately.

Adding an opt-in `diagnostics` view gives HTTP and CLI callers a stable read-only projection of mismatch, manual-review, reconnect-failure, and evaluation-completeness signals while preserving the existing `detailed` and `summary` views.

## What Changes

- Add CLI `bridge watch-status --view diagnostics`.
- Add HTTP `GET /bridge/v1/watch/status?view=diagnostics`.
- Build diagnostics from existing summary rollups only.
- Update focused tests and FUNCTION_TREE B-16/E-09 evidence while keeping both nodes `[部分实现]`.

## Impact

- Affected specs: `tdx-subscription-long-run-status-summary`, `tdx-worker-bridge-http-control-plane`
- Affected code: `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`
