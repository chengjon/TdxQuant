## Context

The existing PingAn trade audit daily/period reports already calculate `acceptance_outcome_coverage_status` from immutable audit artifacts. That object separates automated outcome coverage from full acceptance by setting `live_manual_acceptance_complete=false` and `acceptance_complete=false`.

This change keeps the report read-only but allows operators to provide an explicit JSON manifest that documents manual/live acceptance outcomes. The manifest is only parsed and summarized. It does not drive trade execution, retry, broker control, or status promotion.

## Goals / Non-Goals

**Goals:**

- Accept an optional live/manual acceptance manifest path on daily and period audit reports.
- Validate required PingAn outcome statuses: `confirmed`, `rejected`, `failed`, and `exception`.
- Surface `live_manual_acceptance` details, missing outcomes, invalid entry count, and completion booleans in the existing coverage object.
- Preserve existing default behavior when no manifest path is supplied.
- Keep D-07/D-08 as `[部分实现]` in `FUNCTION_TREE.md`.

**Non-Goals:**

- No real order execution, replay execution, task/bundle workflow execution, or broker readiness probing.
- No automatic promotion of D-07/D-08 to `[已实现]`.
- No attempt to certify production trading readiness, account safety, broker uptime, or UI login readiness.
- No broad redesign of audit aggregation or catalog/report preset registries.

## Decisions

1. Reuse `acceptance_outcome_coverage_status`.

   The existing object already owns the automated-vs-full-acceptance boundary. Adding a `live_manual_acceptance` sub-object keeps the evidence close to the report entries it qualifies and avoids a separate registry that could drift.

2. Use a small JSON manifest.

   The manifest uses schema `tdx.desktop_trade.pingan_live_manual_acceptance.v1` and an `outcomes` array. Each accepted outcome item must include a supported `status` and `accepted=true`. Optional operator/environment fields are copied as evidence metadata.

3. Make completion conjunctive.

   `live_manual_acceptance_complete` is true when the manifest covers every required outcome. `acceptance_complete` is true only when both automated audit coverage and live/manual evidence are complete.

4. Keep invalid evidence non-fatal.

   Missing files, malformed JSON, unsupported schema, and incomplete outcome entries are summarized as `status=invalid` or `status=incomplete` rather than causing the report to fail, so operators can inspect gaps from the same read-only report surface.

## Risks / Trade-offs

- Manifest content is operator-provided and cannot prove real-world truth by itself. The output must keep boundary text that says it is evidence registration, not production readiness.
- Adding a CLI flag to two existing report commands broadens their surface area. The flag is optional and default behavior remains unchanged.
- Completion can become true in synthetic test fixtures. FUNCTION_TREE must still avoid status promotion until all gates, including documented manual/live acceptance process and review, are explicitly accepted.
