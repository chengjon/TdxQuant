## Why

The current architecture has clear domain intent, but several high-change surfaces remain concentrated in shallow modules such as `tdxquant/cli.py`, `tdxquant/api/manager.py`, `tdxquant/api/task.py`, and `tdxquant/api/bridge.py`. This change hardens architecture boundaries so future API, catalog, replay, and trading-capability work can land with better locality and lower regression risk.

## What Changes

- Add an architecture-boundary contract for behavior-preserving modularization of command entrypoints, manager call envelopes, provider/replay seams, runtime configuration validation, and capability risk metadata.
- Move the nested `api` CLI parser and dispatcher toward a dedicated command module while preserving the public `tdxquant.cli` entrypoint and existing command names.
- Introduce a reusable manager call envelope so `TdxApiManager` proxy methods can share timing, replay dispatch, and metadata attachment mechanics without duplicating the pattern per method.
- Add a runtime configuration registry skeleton that centralizes config file discovery and JSON object validation for profiles, presets, catalog, and bundles.
- Add explicit capability risk classification metadata for query/read-only, provider mutation, native trade mutation, and desktop trade mutation surfaces.
- Keep all changes behavior-preserving for existing CLI commands, manager calls, provider result contracts, replay behavior, and tests.

## Capabilities

### New Capabilities
- `tdx-architecture-boundary-hardening`: Defines architectural boundary guarantees for modular command entrypoints, shared manager call mechanics, config registry validation, provider seam direction, and capability risk classification.

### Modified Capabilities
- `tdx-api-cli-entry`: Nested `api` CLI commands must remain behavior-compatible when parser and dispatcher ownership moves into an API command module.
- `tdx-api-management`: Manager-driven calls must use a shared call envelope for timing, replay dispatch, and metadata attachment without changing public result contracts.
- `tdx-command-catalog`: Catalog/config loading may use a central registry, and catalog metadata may expose capability risk classification without changing existing entry execution semantics.
- `tdx-provider-replay-mode`: Replay execution must remain strict and fixture-backed when provider adapter boundaries are introduced or refactored.

## Impact

- Affected code: `tdxquant/cli.py`, new command/config/architecture helper modules, `tdxquant/api/manager.py`, `tdxquant/catalog.py`, `tdxquant/provider_discovery.py`, and focused tests.
- Public behavior: no breaking CLI, manager, provider contract, fixture, or catalog execution behavior changes.
- Risk: refactor risk is highest around CLI parser/dispatcher compatibility and provider envelope payload stability, so the first implementation slice must be covered by existing `test_api_cli.py`, `test_api_manager.py`, and focused new unit tests.
