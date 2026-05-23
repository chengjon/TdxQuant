## Why

Bridge worker HTTP already exposes watch event JSON and SSE stream endpoints, and `bridge_registry.py` already has master-side helper functions. The command-line bridge surface only exposes status/start/stop/list/artifacts/logs, so operators cannot inspect event projections from the same CLI namespace without writing custom code.

## What Changes

- Add `bridge watch-events` as a read-only CLI entry that proxies `/bridge/v1/watch/events`.
- Add `bridge watch-events-stream` as a read-only CLI entry that proxies `/bridge/v1/watch/events/stream` and writes raw SSE text to stdout.
- Preserve existing worker registry, auth, and route semantics; no new scheduling or event contract behavior.
- Update `FUNCTION_TREE.md` E-02 evidence/boundary for the CLI-accessible read-only event projection.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `tdx-api-cli-entry`: Add bridge CLI entries for watch event JSON and SSE stream inspection.

## Impact

- Affected code: bridge CLI parser/handler, CLI tests, `FUNCTION_TREE.md`, and OpenSpec docs.
- No external dependencies.
- No change to bridge HTTP server behavior, worker registry schema, event artifact schema, or replay fixtures.
