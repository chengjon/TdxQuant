## Context

`build_subscription_watch_status_summary()` already emits a stable `boundary` string describing the projection-only status summary behavior. CLI and HTTP summary builders copy only a selected subset of `status_summary`, so callers using summary views cannot see that boundary.

## Decision

Add `boundary` to the `status_summary` allow-list in both summary builders:

- `_build_bridge_watch_status_summary_payload()` in `tdxquant/cli.py`;
- `build_bridge_watch_status_summary_result()` in `tdxquant/bridge_http.py`.

No recomputation is needed. Both surfaces will copy the value already present in detailed `status_summary`.

## Boundaries

- The change is a pure summary projection.
- The change does not start, stop, restart, supervise, schedule retry/backoff, probe providers, stream events, or mutate provider/broker state.
- The change does not alter the boundary text produced by the controller.
- Detailed status and diagnostics payloads remain unchanged except for receiving the already-existing detailed payload.

## Alternatives Considered

- Add a new top-level summary boundary field: rejected because the existing source of truth is `status_summary.boundary`.
- Refactor CLI/HTTP summary builders together: deferred to avoid broadening a one-field parity fix.
