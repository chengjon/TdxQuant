## Why

TdxQuant now has stable provider contracts for synchronous JSON results, capability discovery, block mutation governance, and `subscription-watch` run artifacts, but those contracts still require either live Windows runtime access or ad hoc fixture loading. This blocks offline integration tests and makes upstream contract validation harder than it needs to be.

## What Changes

- Add an in-process replay provider mode that serves supported provider-facing capabilities from built-in fixtures or caller-supplied JSON/JSONL assets instead of live Windows runtime calls.
- Add manager-level provider mode selection so the same Python entrypoints can run in `live` or `replay` mode without introducing parallel replay-only APIs.
- Extend existing CLI entrypoints with replay flags for supported capabilities while preserving current live defaults.
- Add replay materialization for `task subscription-watch` so replay mode immediately writes a completed run artifact bundle from fixture data.
- Define stable default fixture selection and explicit no-live-fallback behavior when replay mode is enabled.

## Capabilities

### New Capabilities
- `tdx-provider-replay-mode`: In-process fake provider mode for supported synchronous provider contracts and `subscription-watch` run artifact replay.

### Modified Capabilities
- `tdx-api-management`: Manager entrypoints gain stable replay-mode configuration and must dispatch supported capabilities through replay without touching live runtime.
- `tdx-api-cli-entry`: CLI entrypoints gain replay-mode flags and must preserve current provider result contracts while switching execution source.
- `tdx-task-subscription-watch`: `subscription-watch` gains replay-mode materialization semantics for completed run artifacts.
- `tdx-provider-replay-fixtures`: Fixture bundle requirements expand from passive samples to replay-mode defaults and supported override sources.

## Impact

- Affected code: `tdxquant/api/manager.py`, domain APIs, CLI argument parsing/dispatch, `tdxquant/replay_fixtures.py`, and new replay-provider helpers.
- Affected task flow: `TdxTaskManager.subscription_watch(...)` and `tdxquant task subscription-watch ...`.
- Affected integration surface: Python manager callers, CLI-driven contract tests, and upstream offline replay/fixture consumers.
- No transport server is introduced in this package; HTTP/SSE replay remains out of scope.
