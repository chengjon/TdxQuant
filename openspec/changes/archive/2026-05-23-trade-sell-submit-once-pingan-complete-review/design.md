## Context

The catalog already exposes:

- `task-sell-submit-once`
- `sell-submit-once-pingan-exception-review`
- `sell-submit-once-pingan-rejection-review`
- `sell-submit-once-pingan-failure-review`
- `buy-submit-once-pingan-complete-review`
- shared success and PingAn confirmed audit report entries

The missing piece is the sell submit-once equivalent of `buy-submit-once-pingan-complete-review`.

## Goals / Non-Goals

**Goals:**

- Register `sell-submit-once-pingan-complete-review` as a fixed catalog bundle.
- Preserve the existing `side=sell` resolution from `task-sell-submit-once`.
- Keep existing sell submit-once PingAn exception/rejection/failure bundles available.

**Non-Goals:**

- Add a new sell submit-once desktop primitive.
- Change `task-sell-submit-once` routing or audit report semantics.
- Add side-specific confirmed audit reports.

## Decisions

- Use `task-sell-submit-once` for the trade step so catalog planning preserves `side=sell`.
- Use `daily-success` and `audit-daily-pingan-confirmed`, matching the existing buy submit-once complete-review pattern.
- Keep this as runtime JSON composition only; code changes are limited to tests and registry evidence.

## Risks / Trade-offs

- The confirmed audit report is broker/status oriented rather than sell-submit-once-specific. This is consistent with the current buy submit-once complete-review bundle and avoids inventing a report preset without evidence of a separate requirement.
