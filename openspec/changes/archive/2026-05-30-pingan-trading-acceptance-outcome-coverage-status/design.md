## Context

The trade audit daily and period report tasks already read immutable audit artifacts and expose by-status aggregation. That makes them the narrowest place to show which PingAn outcomes are represented in the current evidence set, while keeping the workflow read-only and independent of live provider access.

## Goals / Non-Goals

**Goals:**

- Expose `acceptance_outcome_coverage_status` on daily and period trade audit reports.
- Derive the payload only from the report's selected audit entries.
- Make automated outcome coverage and live/manual acceptance status explicit and separate.
- Preserve D-07/D-08 partial status semantics in `FUNCTION_TREE.md`.

**Non-Goals:**

- Do not execute task, report, trade, or bundle steps beyond the existing read-only report generation.
- Do not submit orders or exercise desktop controls.
- Do not invent live/manual acceptance evidence from local audit artifacts.
- Do not move D-07 or D-08 to `[已实现]`.

## Decisions

- Build the coverage payload from the same filtered entries used by the report. This keeps the evidence scoped to the report date or period and avoids global claims from unrelated artifacts.
- Use stable status lists: covered statuses come from the report entries, while required automated statuses are declared explicitly as `confirmed`, `rejected`, `failed`, and `exception`.
- Treat `replayed` as covered evidence when present but not as a replacement for live/manual acceptance. Replay coverage is useful, but it cannot prove live broker acceptance.
- Keep `live_manual_acceptance.status` as `not_provided` for this slice. The field exists to prevent readers from mistaking local report coverage for manual/live acceptance.

## Risks / Trade-offs

- [Risk] A report with many local artifacts could be misread as full acceptance. -> Include `status=partial`, `execution_mode=readonly_report`, `side_effect_level=none`, and explicit missing live/manual acceptance fields.
- [Risk] Required statuses may evolve. -> Keep the list centralized in the task module and make the payload schema explicit.
- [Risk] Exception evidence is not currently a distinct common audit status. -> Include `exception` in missing automated statuses until a later slice records real exception evidence.

