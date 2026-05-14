## Why

`subscription-watch` already has foreground artifacts, worker-local background control, HTTP control-plane endpoints, and reconnect/degraded runtime state. Upstream consumers still need to poll `watch/status` and `watch/events` to observe live updates, and reconnect details remain mostly artifact-level fields instead of transport-visible stream semantics.

This change proposes the first explicit event-stream transport contract for subscription watch without rewriting the canonical `events.jsonl` artifact contract or changing worker registry/auth behavior.

## What Changes

- Add a read-only subscription event-stream transport contract on the worker bridge.
- Define how stream frames project canonical `events.jsonl` rows plus status/reconnect summaries.
- Define resume semantics using stable event IDs / sequence cursors.
- Refine additive reconnect metadata fields for subscription events and stream status frames.
- Add representative transport replay fixtures and focused transport tests.

## Capabilities

### Modified Capabilities

- `tdx-worker-bridge-http-control-plane`
- `tdx-provider-subscription-event-contract`
- `tdx-provider-replay-fixtures`

## Impact

- Affected code:
  - `tdxquant/bridge_http.py`
  - `tdxquant/bridge_registry.py`
  - `tdxquant/subscription_event.py`
  - `tdxquant/replay_fixtures.py`
  - provider fixtures and focused tests
- Affected APIs:
  - worker bridge subscription-watch read transport
  - normalized subscription event-row reconnect metadata
  - replay fixture catalog for stream transport samples
- Explicit non-scope:
  - Do not rewrite `subscription-watch` run artifact layout.
  - Do not change worker registry selection, bearer auth, or `master_allowlist` semantics.
  - Do not introduce multi-worker scheduling or a new provider business capability.

