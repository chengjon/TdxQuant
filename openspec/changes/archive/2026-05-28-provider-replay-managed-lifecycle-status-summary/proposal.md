## Why

E-06 now has managed replay daemon controls, a foreground supervisor loop, opt-in restart/backoff, statefile locking, and process ownership diagnostics. `provider-replay status` still reports lifecycle control as unsupported, which makes the single feature registry and runtime status disagree.

## What Changes

- Update provider replay lifecycle status metadata to distinguish an unconfigured lifecycle statefile from a configured managed replay daemon lifecycle surface.
- When `lifecycle_state_file` is configured, detailed status and summary view should report managed start/stop, daemon supervision, and opt-in restart/backoff as available but operator-driven.
- Keep status read-only: do not start, stop, supervise, inspect process tables, write statefiles, infer port ownership, or claim broker/workflow/write readiness.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`: lifecycle status summary should reflect the already-implemented managed replay daemon lifecycle surface when the statefile path is configured.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`, `tdxquant/cli.py`.
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`.
- Documentation registry: `FUNCTION_TREE.md` E-06 evidence and boundary notes.
