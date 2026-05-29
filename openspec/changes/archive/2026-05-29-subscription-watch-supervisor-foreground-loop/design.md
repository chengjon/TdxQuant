## Context

`supervisor_tick()` gives operators a safe single recovery step after restart backoff expires. A human operator still has to repeat the call manually while waiting for a backoff window. A bounded foreground loop is the smallest next step: it automates repeated explicit ticks inside the current process, but it does not become a daemon or scheduler.

## Goals / Non-Goals

**Goals:**

- Run at most `max_ticks` calls to `supervisor_tick()`.
- Sleep between waiting ticks only when `interval_seconds > 0` and another tick remains.
- Stop early on `recovered`, `no_action`, or a failed tick result.
- Return stable compact tick summaries with count, final status, final decision, and boundary.
- Expose HTTP/registry/CLI dispatch with explicit `max_ticks`, `interval_seconds`, and optional `reason`.

**Non-Goals:**

- No background daemon, timer, scheduler, worker process, or service manager.
- No automatic invocation from `status`, `restart`, `supervisor_tick`, event stream, or catalog.
- No start/stop/restart calls except whatever the existing `supervisor_tick()` performs.
- No health/readiness proof, PID ownership proof beyond existing diagnostics, or real provider lifecycle completion.
- No workflow/task/report/trade execution.

## Decisions

- Keep the loop in `SubscriptionWatchBackgroundController` so it reuses the current tick implementation and its backoff/start boundaries.
- Name the public method `supervisor_run()` and bridge route `POST /bridge/v1/watch/supervisor-run` to make the foreground operator action explicit.
- Keep validation local and strict: `max_ticks` must be positive; `interval_seconds` must be non-negative.
- Return `ok: true` when the foreground run itself completes, even if a tick summary reports a failed tick; invalid run parameters return `ok: false` with `INVALID_REQUEST`.

## Risks / Trade-offs

- [Risk] A loop can be mistaken for long-running governance. -> The result boundary and FUNCTION_TREE entry state this is foreground, bounded, and operator-triggered only.
- [Risk] Repeated waiting ticks could hammer status. -> `max_ticks` is mandatory/finite and sleeps only between bounded iterations.
- [Risk] Tick failures could be hidden by top-level success. -> Each tick summary includes `ok`, `error_code`, and final status/decision reflects the last tick.

