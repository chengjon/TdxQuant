## Context

`SubscriptionWatchBackgroundController` already owns the daemon lifecycle scaffold:

- `start_supervisor_daemon(...)`
- `supervisor_daemon_status()`
- `stop_supervisor_daemon(...)`

The previous slice intentionally did not expose HTTP, registry, CLI, catalog, task, report, trade, or workflow entrypoints. This change exposes only the manual bridge control surfaces required for an operator to inspect or drive that scaffold.

## Decisions

- Use dedicated routes under `/bridge/v1/watch/supervisor-daemon/*` instead of overloading existing `supervisor-tick` or `supervisor-run` routes.
- Keep daemon status as `GET` and daemon start/stop as `POST`.
- Keep request bodies small and explicit:
  - start: `max_ticks`, optional `interval_seconds`, optional `loop_sleep_seconds`, optional `reason`, optional `owner_token`
  - stop: `owner_token`, optional `reason`
- Preserve controller result envelopes exactly as returned by the worker-local controller.
- Put CLI subcommands under `tdxquant bridge` beside the existing watch supervisor controls:
  - `watch-supervisor-daemon-status`
  - `watch-supervisor-daemon-start`
  - `watch-supervisor-daemon-stop`

## Boundaries

- This does not enable daemon autostart.
- This does not implement automatic restart/backoff policy.
- This does not execute task/report/trade/workflow/catalog steps.
- This does not prove provider readiness, broker readiness, live data availability, port ownership, or Windows process-manager integration.
- This does not change existing `watch-status`, `watch-supervisor-tick`, or `watch-supervisor-run` semantics.

## Verification

- Red tests first for HTTP route dispatch, registry URL/body dispatch, and CLI parser/dispatch.
- Focused pytest over bridge HTTP, bridge registry, and API CLI tests.
- `openspec validate --all --strict`.
- `git diff --check`.
- `python scripts/validate_function_tree_registry.py`.
