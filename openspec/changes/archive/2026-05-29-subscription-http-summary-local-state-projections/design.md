## Context

`tdxquant/cli.py` and `tdxquant/bridge_http.py` each build a compact summary view from detailed watch status payloads. The CLI summary builder already copies `statefile_ownership` and `supervisor_daemon` from `status_summary`. The HTTP summary builder still copies only the older status keys and separately projects top-level `supervisor_daemon`.

## Decision

Update `build_bridge_watch_status_summary_result()` to include `statefile_ownership` and `supervisor_daemon` in the `status_summary` allow-list.

For top-level `supervisor_daemon`, keep the existing projection behavior unchanged. For `status_summary.statefile_ownership`, trust the controller-created compact projection already present in detailed `status_summary`; do not recompute ownership or acquire locks in the HTTP layer.

## Boundaries

- HTTP summary remains a pure projection of the detailed status payload.
- The change does not call start/stop/restart/supervise/backoff/probe or event-stream behavior.
- The change does not expose raw statefile content, owner token, command settings, lock handles, or provider/broker readiness claims.
- The change does not alter detailed status or diagnostics output.

## Alternatives Considered

- Refactor CLI and HTTP summary builders into one helper: deferred because it would broaden the diff; this slice only closes the parity gap.
- Put local-state fields at top-level only: rejected because `status_summary` is the single compact long-run summary contract for these projections.
