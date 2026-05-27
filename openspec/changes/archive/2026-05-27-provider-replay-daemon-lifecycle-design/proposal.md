# provider replay daemon lifecycle design

## Why

E-06 currently has a replay-only fake provider, read-only status/config checks, opt-in probes, and summary views. It deliberately does not own daemon lifecycle. That boundary is repeated across the implementation and `FUNCTION_TREE.md`, but the future lifecycle surface is not yet captured as a single design contract.

This design-only change records the intended lifecycle scope before any implementation: start, stop, status, restart, and backoff must be separately introduced as explicit lifecycle management work, not inferred from the existing read-only provider-replay status/probe features.

## What Changes

- Add an OpenSpec design contract for future provider-replay daemon lifecycle control.
- Define operation boundaries for:
  - `start`
  - `stop`
  - lifecycle `status`
  - explicit `restart`
  - restart/backoff policy
- Preserve the current behavior as non-lifecycle-managing:
  - existing `provider-replay status` remains read-only
  - existing probes remain opt-in
  - existing summary/advisory fields remain observational
  - no start/stop/restart/backoff code is added in this change
- Update `FUNCTION_TREE.md` E-06 as `[部分实现]` with a clearly marked designed/pending lifecycle contract.

## Impact

- Affected specs: `tdx-provider-transport-replay-service`
- Affected registry: `FUNCTION_TREE.md`
- No runtime code changes
- No CLI lifecycle command implementation
- Verification: OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation

