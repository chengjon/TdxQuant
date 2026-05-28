# Provider Replay Managed Daemon Control Design

## Context

The current provider replay lifecycle code can write and check a locked statefile with owner token, generation, config hash, PID, and state. Lifecycle readiness remains blocked because no actual managed process control exists.

## Approach

Add a minimal control layer in `tdxquant/provider_transport_replay.py`.

Start:

- Require `lifecycle_state_file`.
- Check any existing statefile.
- If the statefile is valid for this config and its PID is running, return `already_running` without spawning a second daemon.
- Otherwise launch `[python, -m, tdxquant.cli, provider-replay, serve, --config, <path>]` in the background.
- Generate or accept an owner token.
- Write the statefile with `state=running`, the spawned PID, owner token, generation, and config hash.
- If statefile writing fails, terminate the just-spawned process and return an error result.

Status:

- Read the existing statefile using current diagnostics.
- Check PID liveness only when diagnostics identify a valid PID.
- Report `running`, `not_running`, `missing`, `invalid`, or `not_configured`.
- Never mutate state.

Stop:

- Require an owner token.
- Validate statefile schema, provider id, config hash, statefile staleness, and owner token.
- Check PID liveness.
- Send a termination signal only to the recorded PID.
- Write `state=stopping` with the same owner token and incremented generation.
- Return a structured result.

## Testability

The helper functions accept fake process launcher, liveness checker, and terminator callables so tests do not need to start or kill real long-running processes.

## Boundaries

This is one-shot managed control, not supervision. It does not restart failed daemons, keep a monitoring loop, infer process ownership from ports, inspect process command lines, manage real providers, or assert broker/workflow/write readiness.

