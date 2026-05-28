# Provider Replay Daemon Supervisor Loop Design

## Context

The managed daemon control layer can start a background replay daemon, check statefile/PID status, and stop an owned PID. There is not yet a long-running process that owns observation over the child and refreshes statefile heartbeat.

## Approach

Add `run_provider_replay_managed_daemon_supervisor()` in `tdxquant/provider_transport_replay.py`.

The helper will:

- Launch `provider-replay serve --config <path>` using the same command builder as managed start.
- Generate or accept an owner token.
- Write a lifecycle statefile with `state=supervising`.
- Poll the child process with `process.poll()` on a fixed interval.
- Refresh the statefile on each heartbeat with `state=supervising`.
- When the child exits, write `state=exited` and include exit code in the result.
- If interrupted, terminate the child and write `state=stopping`.

For tests, the helper accepts `popen_factory`, `sleep`, `max_heartbeats`, and `updated_at_factory` callables/values.

## Boundaries

The supervisor is foreground and conservative. It observes one child process and updates statefile heartbeat. It does not restart the child, schedule backoff, infer process ownership from ports, validate broker readiness, or manage real providers.

