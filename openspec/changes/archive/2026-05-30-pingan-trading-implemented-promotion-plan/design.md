## Context

D-07 and D-08 cover high-risk desktop trading paths. Current FUNCTION_TREE evidence is deliberately limited to stable catalog discovery, non-executing plan/preview summaries, task/CLI entry registration, and audit/capability metadata. The next status transition requires real execution evidence and stronger safety gates.

## Goals / Non-Goals

**Goals:**

- Define a promotion sequence for D-07/D-08 before `[已实现]`.
- Keep `FUNCTION_TREE.md` the single registry of current status, evidence, and boundary.
- Prevent catalog-only evidence from being interpreted as production readiness.

**Non-Goals:**

- Do not execute live buy/sell/confirm_current/submit_once workflows.
- Do not change order submission behavior.
- Do not mark D-07 or D-08 `[已实现]`.
- Do not create `ROADMAP.md` or any competing truth source.

## Decisions

Promotion to `[已实现]` must be a later OpenSpec implementation change with this order:

1. Provider and broker ownership gates: explicit environment prerequisites, process/window ownership, and live-provider capability probes.
2. Safety gates: max price/quantity/submission-key checks, idempotency, dry-run separation, and manual approval semantics.
3. Desktop lifecycle gates: deterministic dialog readiness, result/exception popup coverage, timeout/retry behavior, and confirm_current ownership.
4. Audit gates: immutable submission/audit evidence for success, failure, rejection, exception, and replay inspection.
5. Acceptance gates: focused automated tests for fake/replay paths plus explicitly documented manual/live acceptance evidence when required.
6. FUNCTION_TREE transition: only after the above evidence is present should D-07/D-08 status move from `[部分实现]` to `[已实现]`.

## Risks / Trade-offs

- This change intentionally does not produce a user-facing execution feature. Its value is reducing status drift before high-risk trading implementation begins.
- Some acceptance gates may require a real Windows/TongDaXin/PingAn environment and must not be simulated as production evidence.
