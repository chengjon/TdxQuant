## Context

`SubscriptionWatchBackgroundController.supervisor_run()` is currently bounded and foreground-only. Operators can invoke it explicitly, but no local process owns a recurring supervisor loop. The next step toward long-run governance is a separate supervisor daemon scaffold with its own statefile, pidfile, and lockfile so it does not corrupt the existing subscription-watch active run control files.

This change introduces explicit opt-in local lifecycle control only. The daemon process runs the existing bounded supervisor loop repeatedly, but nothing starts it automatically and no bridge, CLI, catalog, or task entrypoint is added in this slice.

## Goals / Non-Goals

Goals:

- Add fixed supervisor daemon state/pid/lock paths separate from `active.json`, `pid`, and `lock`.
- Add controller methods for explicit `start_supervisor_daemon()`, `supervisor_daemon_status()`, and `stop_supervisor_daemon()`.
- Start writes an owned running statefile and pidfile after launching the daemon command.
- Status is read-only and derives running/not-running/missing/invalid from statefile plus pid liveness.
- Stop requires a matching owner token before signaling the recorded pid and writing a stopping state.
- Add a runner module that repeatedly calls `supervisor_run(max_ticks, interval_seconds, reason)` with a bounded loop sleep.

Non-goals:

- No HTTP, CLI, bridge registry, catalog, task, report, trade, or workflow entrypoint.
- No automatic daemon start from status/restart/tick/run/watch/event paths.
- No restart/backoff policy wiring beyond calling the already explicit `supervisor_run()` inside an explicitly started daemon process.
- No provider readiness, broker readiness, or live availability assertion.
- No history ledger or raw provider payload exposure.

## Decisions

- Use `supervisor.json`, `supervisor.pid`, and `supervisor.lock` under the existing root directory. Keeping paths separate prevents the supervisor lifecycle from overwriting subscription-watch run ownership.
- Return stable envelopes with schema version `tdx.subscription_watch.supervisor_daemon.v1`.
- Use owner tokens for stop authorization. A missing or mismatched token blocks signaling the pid.
- Build the daemon command as `python -m tdxquant.subscription_watch_supervisor_daemon --root-dir ...`, with explicit `--max-ticks`, `--interval-seconds`, `--loop-sleep-seconds`, and optional `--reason`.
- Keep daemon status read-only. It does not call `supervisor_tick()`, `supervisor_run()`, `start()`, `stop()`, or `restart()`.

## Risks / Trade-offs

- The daemon runner is intentionally minimal; it loops forever until process termination. Backoff/restart policy tuning remains a later OpenSpec slice.
- Status uses local pid liveness and statefile owner evidence only. It does not prove provider health, quote delivery, or broker availability.
- No HTTP/CLI entrypoint means the first slice is mostly internal and test-driven. That keeps the lifecycle semantics small before exposing operator controls.
