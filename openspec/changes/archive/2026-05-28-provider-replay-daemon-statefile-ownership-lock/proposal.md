# Provider Replay Daemon Statefile Ownership Lock

## Why

E-06 currently exposes only read-only lifecycle status, plan, statefile-check, and readiness summaries. Later daemon start/stop, supervisor, restart/backoff, and real provider lifecycle control all need a safe local ownership primitive first. Without an atomic statefile writer and lock, lifecycle control cannot distinguish a tool-owned replay daemon from an unrelated process or stale file.

## What Changes

Add a provider replay lifecycle statefile writer that records ownership metadata under an exclusive lock and atomically replaces the configured statefile.

- Add an internal provider replay lifecycle statefile payload builder.
- Add a statefile writer that acquires an exclusive lock file before writing.
- Include ownership fields: schema version, provider id, pid, lifecycle state, owner token, generation, config hash, and updated timestamp.
- Extend read-only statefile diagnostics to surface ownership fields when present.
- Add tests proving atomic write output, lock exclusion, and diagnostics compatibility.
- Update `FUNCTION_TREE.md` E-06 evidence and boundary without claiming daemon lifecycle control.

## Non-Goals

- No `provider-replay daemon start/stop/restart` command.
- No process spawning or killing.
- No long-running supervisor loop.
- No restart/backoff scheduling.
- No PID liveness or process table ownership proof.
- No port ownership inference.
- No real provider or broker lifecycle management.
- No change to provider replay HTTP endpoints.
