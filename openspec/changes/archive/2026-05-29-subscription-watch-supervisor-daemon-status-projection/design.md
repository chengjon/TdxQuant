## Context

The previous slices introduced:

- controller-local supervisor daemon scaffold and state files;
- explicit bridge HTTP/registry/CLI control routes for manual daemon status/start/stop.

The default `watch-status` detailed, summary, and diagnostics views still focus on foreground subscription-watch runs. This makes it hard to inspect daemon ownership and liveness while staying inside the existing operator status surface.

## Decisions

- Reuse `SubscriptionWatchBackgroundController.supervisor_daemon_status()` from `status()` instead of duplicating file parsing.
- Store only the status result payload under `supervisor_daemon` in the detailed status response.
- Project a compact, non-sensitive summary in bridge summary and diagnostics views:
  - schema version, daemon status, state, statefile/pidfile validity, pid, process liveness, generation, owner-token presence, control allowance, and boundary.
- Do not expose raw `owner_token`, full `settings`, daemon command, or file paths in bridge summary/diagnostics.
- Keep the status read model additive and best-effort: a malformed/missing daemon state remains a status value, not a thrown lifecycle action.

## Boundaries

- This is read-only status projection.
- This does not start, stop, restart, supervise, schedule backoff, or modify any statefile.
- This does not infer port ownership, Windows service ownership, provider readiness, broker readiness, or workflow readiness.
- This does not change the explicit `watch-supervisor-daemon-*` control commands or their ownership checks.

## Verification

- Red tests first for controller status, HTTP summary view, and HTTP diagnostics view.
- Focused pytest over subscription background and bridge HTTP tests.
- `openspec validate --all --strict`.
- `git diff --check`.
- `python scripts/validate_function_tree_registry.py`.
