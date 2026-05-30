## Context

The existing coverage payload already derives covered and missing statuses from selected immutable audit entries. Once confirmed, rejected, failed, and exception entries are all present, the automated portion can be complete while live/manual acceptance remains absent.

## Goals / Non-Goals

**Goals:**

- Expose `automated_outcome_coverage_complete` in daily and period coverage payloads.
- Expose live/manual acceptance completion separately.
- Keep report generation read-only and scoped to selected audit entries.
- Preserve D-07/D-08 partial status semantics in `FUNCTION_TREE.md`.

**Non-Goals:**

- Do not execute trades or desktop controls.
- Do not generate manual/live acceptance evidence.
- Do not change audit artifact schemas.
- Do not mark D-07 or D-08 `[已实现]`.

## Decisions

- Derive `automated_outcome_coverage_complete` from whether `missing_automated_outcome_statuses` is empty.
- Add `live_manual_acceptance_complete=false` beside the existing `live_manual_acceptance.status=not_provided` so callers can distinguish automated coverage from full acceptance.
- Keep `acceptance_complete=false` for this slice because live/manual acceptance is still required.

## Risks / Trade-offs

- [Risk] A true automated coverage flag could be mistaken for final acceptance. -> Keep separate live/manual fields and boundary text.
- [Risk] Empty report periods could look complete if the logic is wrong. -> Completion is based on an empty missing list after checking all required statuses, not on absence of entries.

