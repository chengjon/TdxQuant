# Proposal

## What Changes

Add a compact read-only `diagnostics.restartability` projection to subscription watch-status diagnostics views.

The change adds:

- Diagnostics restartability fields derived from the existing detailed status payload and summary view.
- HTTP and CLI diagnostics coverage for active-with-start-request, missing metadata, and blocked restartability cases.
- FUNCTION_TREE B-16/E-09 evidence and boundary updates while keeping the nodes `[部分实现]`.

## Why

The explicit restart and restart-preflight endpoints are now available, but the diagnostics view remains blind to restartability. Operators should be able to inspect the same high-level restartability posture from the diagnostics view without triggering lifecycle control or calling a separate endpoint.

## Scope

- Specs: `tdx-subscription-long-run-status-summary`, `tdx-worker-bridge-http-control-plane`.
- Code: `tdxquant/subscription_watch_status_diagnostics.py`, `tdxquant/bridge_http.py`, `tdxquant/cli.py`.
- Tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`.
- Registry: `FUNCTION_TREE.md`.
