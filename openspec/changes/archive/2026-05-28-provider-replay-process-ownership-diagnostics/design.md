# Provider Replay Process Ownership Diagnostics Design

## Context

`get_provider_replay_managed_daemon_status()` currently reports statefile diagnostics and whether the recorded PID is running. It does not provide a single ownership decision explaining whether the process is controlled by the current config and owner token. `lifecycle-readiness` also still treats owned process identity as missing even when statefile diagnostics and PID liveness are known.

## Approach

Add `build_provider_replay_process_ownership_diagnostics()` in `tdxquant/provider_transport_replay.py`.

Inputs:

- Existing statefile diagnostics.
- Optional expected owner token.
- Optional `process_running(pid)` hook.
- Optional `process_identity_matches(pid, command)` hook.

The helper returns:

- `ownership_status`: `owned`, `not_configured`, `missing_statefile`, `invalid_statefile`, `stale_statefile`, `process_not_running`, `owner_token_mismatch`, `config_hash_mismatch`, `process_identity_mismatch`, or `unknown_process_identity`.
- `owned_process`: boolean.
- `pid`, `pid_live`, `owner_token_present`, `owner_token_matches`, `config_hash_matches`, `process_identity_checked`, `process_identity_matches`.
- `control_allowed`: true only for `owned`.
- A read-only boundary string.

Wire this diagnostic into managed daemon status. Then allow lifecycle readiness to count `owned_process_identity` as satisfied only when ownership diagnostics say `owned`, while leaving other missing requirements intact.

## Boundaries

The diagnostic is read-only. It does not kill processes, infer ownership from ports, enable default command-line inspection, recover providers, or prove broker/workflow/write readiness.

