## Context

The catalog already exposes ordinary sell PingAn exception/rejection/failure review bundles:

- `sell-pingan-exception-review`
- `sell-pingan-rejection-review`
- `sell-pingan-failure-review`

It also exposes the shared success and PingAn confirmed audit report entries:

- `daily-success`
- `audit-daily-pingan-confirmed`

The missing piece is the ordinary sell equivalent of `buy-pingan-complete-review`.

## Goals / Non-Goals

**Goals:**

- Register `sell-pingan-complete-review` as a fixed catalog bundle.
- Keep the bundle routed through existing task and report entries.
- Keep existing ordinary sell PingAn exception/rejection/failure bundles available.

**Non-Goals:**

- Add a new trade manager method, desktop automation primitive, report preset, or audit status.
- Change the semantics of existing sell task execution.

## Decisions

- Use `task-sell` for the trade step so the bundle stays on the ordinary sell task path.
- Use `daily-success` and `audit-daily-pingan-confirmed` for success review, matching the existing buy and confirm_current complete-review pattern.
- Keep this as runtime JSON composition only; code changes are limited to tests and registry evidence.

## Risks / Trade-offs

- The shared `audit-daily-pingan-confirmed` report is not sell-specific. This matches the existing catalog model, where confirmed trade audit review is broker/status oriented rather than side-specific.
