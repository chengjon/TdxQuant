# provider-transport-replay-cli-entry

## Why

`FUNCTION_TREE.md` E-05 records that the provider HTTP replay service exists as a fixture-backed, read-only transport surface, but the current operator path is still Python/API oriented. There is no stable CLI entry that loads the replay service config and starts the existing foreground server, which makes the service harder to discover and run in local contract tests.

This change adds a narrow CLI entry for the existing replay transport service. It does not add daemon lifecycle management, background supervision, live provider fallback, or new business capabilities.

## What Changes

- Add `provider-replay serve --config <path>` as a foreground CLI entry.
- Add `provider-replay config-check --config <path>` for non-blocking validation and machine-readable config summary.
- Add a runtime example config for local replay service startup.
- Cover parser and handler behavior with focused tests.
- Update `FUNCTION_TREE.md` E-05 evidence and boundary.

## Capabilities

### Modified Capabilities

- `tdx-provider-transport-replay-service`
- `tdx-api-cli-entry`

## Impact

- No changes to replay HTTP endpoint behavior.
- No daemon start/stop lifecycle; `serve` runs in the foreground and returns the underlying server exit code.
- No live Windows provider access is introduced.

