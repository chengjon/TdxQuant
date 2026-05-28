# Provider Replay Daemon Restart Backoff Policy Design

## Context

`run_provider_replay_managed_daemon_supervisor()` currently launches one child, refreshes `state=supervising`, writes `state=exited` on child exit, and stops. This is safe but cannot recover from a transient replay daemon failure.

## Approach

Add optional policy parameters to the supervisor helper:

- `restart_policy`: `never` or `on-failure`.
- `max_restarts`: non-negative integer.
- `backoff_seconds`: non-negative fixed sleep before retry.

The default remains `restart_policy=never`, preserving current behavior. When `on-failure` is selected:

- Exit code `0` remains terminal success and writes `state=exited`.
- Non-zero exit codes trigger a restart only while `restart_count < max_restarts`.
- Before retry sleep, the helper writes `state=backoff`.
- After retry, the helper launches a new child and writes `state=supervising`.
- If a non-zero exit occurs after the restart budget is exhausted, the helper writes `state=failed` and returns `supervisor_status=restart_exhausted`.

The existing fake process/sleep/timestamp hooks remain the test seam.

## Boundaries

The policy is in-memory for one foreground supervisor invocation. It does not persist restart budget across supervisor runs, use exponential backoff, inspect process command lines, infer ownership from ports, recover real providers, or assert broker/workflow/write readiness.

