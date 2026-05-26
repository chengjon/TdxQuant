# Proposal: Subscription Summary Runtime PID Source

## Why

`runtime.pid` is already present in the compact summary view when `control.pid` is available, but unlike `runtime.run_id` it does not state its source. Adding `runtime.pid_source` makes the summary identity projection more auditable and prevents readers from treating PID as a merged or provider-derived value.

## What Changes

- Include `runtime.pid_source` with value `control` whenever `runtime.pid` is included from `control.pid`.
- Cover both bridge HTTP summary view and CLI summary view.
- Update tests, OpenSpec, and `FUNCTION_TREE.md` evidence/boundary.

## Non-Goals

- Do not change PID source precedence or add PID fallback from `watch_status`.
- Do not compare process ownership or add PID liveness/readiness checks.
- Do not change reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.
- Do not expose raw payloads in summary view.
