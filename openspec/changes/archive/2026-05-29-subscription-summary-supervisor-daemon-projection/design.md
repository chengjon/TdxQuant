## Context

`SubscriptionWatchBackgroundController.status()` already computes a top-level `supervisor_daemon` read model by calling `supervisor_daemon_status()` and projecting it through `build_supervisor_daemon_status_projection()`. `build_subscription_watch_status_summary()` currently receives only control/watch status inputs, so summary consumers do not get the daemon read model even though detailed status has it.

This change keeps the daemon lifecycle model explicit and opt-in. It only reuses the existing read-only daemon status projection in the summary payload.

## Decision

Extend `build_subscription_watch_status_summary()` with an optional `supervisor_daemon` argument. The function will:

- normalize the argument with `build_supervisor_daemon_status_projection()`;
- include `status_summary.supervisor_daemon` only when the projection is non-empty;
- preserve the existing boundary string and governance logic.

`SubscriptionWatchBackgroundController.status()` will pass its existing projected `supervisor_daemon` into summary construction so detailed status and summary status share the same read model source.

Bridge summary output will keep using `_build_bridge_watch_status_summary_payload()`. Because it already copies selected `status_summary` keys, it will explicitly add `supervisor_daemon` to that allow-list.

## Boundaries

- The projection is read-only and derived from existing local supervisor daemon statefile/pidfile diagnostics.
- The projection does not call daemon start/stop, background supervisor loops, restart, backoff, provider probes, broker functions, or event streams.
- The projection does not claim provider readiness, trading readiness, live行情 availability, or production lifecycle health.
- The top-level detailed `supervisor_daemon` payload remains available and unchanged.

## Alternatives Considered

- Put daemon fields only under `runtime`: rejected because these fields describe the explicit supervisor daemon, not the active watch run identity.
- Add another CLI command: rejected because `watch-supervisor-daemon-status` already exists; this change is about summary projection consistency.
