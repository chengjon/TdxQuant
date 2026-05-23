## Context

The watch status payload already includes a detailed `status_summary` object. Recent governance work added `status_summary.governance.action_summary`, but `bridge watch-status` still emits the whole detailed response by default.

Catalog commands already use `--view summary` for compact output. This change applies the same explicit view pattern to `bridge watch-status`.

## Goals / Non-Goals

**Goals:**

- Add an opt-in summary view for `bridge watch-status`.
- Keep the existing detailed output as the default.
- Surface governance `decision`, `requires_manual_review`, and `action_summary` in the summary view.

**Non-Goals:**

- Change bridge HTTP routes or worker responses.
- Change subscription watch controller status semantics.
- Trigger reconnect, restart, backoff, or lifecycle changes.
- Add summary views for other bridge subcommands.

## Decisions

- Implement the summary view in the CLI layer, after `run_bridge_watch_status()` returns. This keeps bridge registry and HTTP behavior untouched.
- Preserve the envelope shape: summary output remains a JSON payload with `ok`, `result`, and optional `error`.
- Include a small `result` object with `mode`, `worker`, `status`, `status_summary`, and `governance` fields. The governance sub-object is copied from `status_summary.governance` when present.

## Risks / Trade-offs

- Summary output is intentionally lossy. Operators who need raw control/watch_status details should keep the default detailed view.
