# Provider Replay Daemon Supervisor Loop

## Why

E-06 now has locked statefile ownership and one-shot managed daemon start/status/stop. It still lacks a long-running owner process that keeps the managed replay daemon observed and refreshes lifecycle heartbeat state. Adding a conservative foreground supervisor loop is the next step before any restart/backoff policy.

## What Changes

- Add a managed daemon supervisor helper that launches the replay daemon, writes `state=supervising`, refreshes heartbeat state, observes child process exit, and writes an exit state.
- Add `provider-replay daemon supervise` CLI entry.
- Keep supervisor execution foreground and explicit.
- Add tests using fake process and fake sleep hooks so no real long-running process is launched.
- Update `FUNCTION_TREE.md` E-06 evidence and boundary.

## Non-Goals

- No automatic restart or backoff scheduling.
- No recovery loop after child exit.
- No port ownership inference.
- No real provider or broker lifecycle management.
- No broker/workflow/write readiness claim.

