# Proposal

## What Changes

Add a read-only subscription-watch restart preflight view that tells an operator whether the currently active background run has enough persisted control state to be explicitly restarted.

The change adds:

- A controller-level `restart_preflight()` result derived from reconciled active state and persisted `start_request`.
- A worker bridge HTTP endpoint for the preflight view.
- A registry helper and CLI command for operator discovery.
- FUNCTION_TREE B-16/E-09 evidence and boundary updates while keeping the nodes `[部分实现]`.

## Why

Explicit restart now exists, but operators currently discover missing `start_request` or inactive-run failures only by attempting restart. A read-only preflight view makes the restart boundary inspectable before mutation and keeps B-16/E-09 progress focused on discoverability and governance evidence rather than automatic lifecycle policy.

## Scope

- Specs: `tdx-task-subscription-watch-background-control`, `tdx-worker-bridge-http-control-plane`.
- Code: `tdxquant/subscription_watch_background.py`, `tdxquant/bridge_http.py`, `tdxquant/bridge_registry.py`, `tdxquant/cli.py`.
- Tests: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`, `tests/test_bridge_registry.py`, `tests/test_api_cli.py`.
- Registry: `FUNCTION_TREE.md`.
