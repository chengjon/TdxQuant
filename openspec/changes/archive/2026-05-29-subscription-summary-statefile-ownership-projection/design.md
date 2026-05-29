## Context

`SubscriptionWatchBackgroundController.status()` already builds a top-level `statefile_ownership` diagnostic with `build_background_statefile_ownership()`. The diagnostic is compact and read-only, but `build_subscription_watch_status_summary()` currently does not receive it, so summary payloads omit local ownership evidence.

This change mirrors the existing supervisor daemon summary projection pattern and keeps ownership evidence under the same explicit local-state boundary.

## Decision

Extend `build_subscription_watch_status_summary()` with an optional `statefile_ownership` argument. The function will:

- copy a compact subset of the existing diagnostic into `status_summary.statefile_ownership`;
- include the projection only when the diagnostic is a dictionary;
- avoid exposing raw statefile content or any lock handle;
- keep governance decisions and lifecycle behavior unchanged.

`SubscriptionWatchBackgroundController.status()` will pass the existing top-level `statefile_ownership` diagnostic into summary construction.

Bridge summary output will explicitly allow `statefile_ownership` in the copied `status_summary` keys.

## Boundaries

- The projection is read-only and derived from existing local statefile/pidfile diagnostics.
- The projection does not acquire the control lock, start/stop/restart a worker, run supervisor loops, schedule retry/backoff, probe providers, or mutate broker/provider state.
- The projection does not claim provider readiness, trading readiness, live行情 availability, production lifecycle health, or process ownership beyond local PID evidence.
- The top-level detailed `statefile_ownership` payload remains available and unchanged.

## Alternatives Considered

- Put ownership fields under `runtime`: rejected because the fields describe local control-file ownership evidence, not the active watch run identity.
- Keep summary view unchanged: rejected because compact operators already use summary view for B-16/E-09 governance posture, and local ownership mismatch is a core long-run diagnostic.
