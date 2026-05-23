## Context

The provider transport replay service already exposes a fixture-backed HTTP surface and foreground CLI startup. E-06 remains partial because this surface simulates read-only fake-provider responses but does not own process lifecycle, scheduling, restart, or live market sessions.

## Goals / Non-Goals

**Goals:**

- Provide a stable status summary that callers can inspect before running the replay service.
- Make fake-provider lifecycle boundaries machine-readable: foreground process only, no managed daemon start/stop.
- Reuse the existing config loader and config summary path.

**Non-Goals:**

- No background process manager, pid registry, scheduler, reconnect policy, or restart loop.
- No live TongDaXin or Windows runtime integration.
- No mutation or provider write surface.

## Decisions

- Add a pure `build_provider_transport_replay_status(config)` helper in `provider_transport_replay.py`.
  - Rationale: the status is derived from config and static endpoint coverage, so it should be testable without sockets.
  - Alternative considered: start the HTTP server and call a status endpoint. That would make status discovery more expensive and blur the no-lifecycle-management boundary.
- Expose the helper through `provider-replay status --config <path>`.
  - Rationale: the CLI already has `serve` and `config-check`; a non-serving status command gives operators a safe discovery path.
  - Alternative considered: extend `config-check`. Keeping `status` separate prevents config validation from silently becoming capability/lifecycle reporting.
- Keep the FUNCTION_TREE status as `[部分实现]`.
  - Rationale: the change improves evidence and boundary clarity, but still does not implement daemon lifecycle management.

## Risks / Trade-offs

- Status may be mistaken for a live health probe -> include `runtime_observed: false` and `start_stop_managed: false` fields.
- Endpoint coverage can drift as the service evolves -> keep endpoint names in one helper and cover them in tests.
