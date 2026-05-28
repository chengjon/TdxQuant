# Provider Replay Daemon Statefile Ownership Lock Design

## Context

The existing provider replay lifecycle surface is intentionally read-only. `build_provider_transport_replay_status()` reports lifecycle control as unsupported, `check_provider_replay_lifecycle_statefile()` reads an optional configured statefile, and CLI plan/readiness commands keep control blocked. E-06 cannot safely advance toward daemon lifecycle control until the local ownership record is writable, locked, and machine-verifiable.

## Approach

Add a small internal statefile ownership layer in `tdxquant/provider_transport_replay.py`.

The writer will:

- Require `config.lifecycle_state_file`.
- Build a canonical payload with `schema_version`, `provider_id`, `pid`, `state`, `owner_token`, `generation`, `config_hash`, and `updated_at`.
- Compute `config_hash` from non-secret config identity plus a token hash, without storing the raw token.
- Acquire an exclusive `<statefile>.lock` file via `O_CREAT | O_EXCL`.
- Write a temporary JSON file in the statefile directory.
- Replace the target statefile with `os.replace()`.
- Remove the lock file on completion or failure.
- Return a structured result instead of dispatching lifecycle control.

The read-only checker will remain backward-compatible with existing minimal statefiles. Ownership fields are reported when present. Missing ownership fields in older statefiles do not invalidate those files in this slice because validation strictness will be introduced only after daemon start/stop owns the full lifecycle contract.

## Boundaries

This change is not daemon lifecycle control. It does not start, stop, supervise, restart, inspect, or recover any process. A successful statefile write only proves the writer could acquire the statefile lock and atomically persist a local ownership payload. PID liveness, process ownership, supervisor health, and readiness are later slices.

