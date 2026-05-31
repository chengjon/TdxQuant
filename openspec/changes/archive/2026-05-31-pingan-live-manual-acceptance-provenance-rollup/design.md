## Context

`TdxTaskManager.pingan_live_manual_acceptance(...)` writes a controlled live/manual acceptance artifact, and audit report coverage can consume that artifact as part of `acceptance_outcome_coverage_status`. The promotion readiness rollup currently validates provenance for the top-level evidence files (`preflight`, `dialog_readiness`, and `acceptance_coverage`) but does not distinguish whether the nested live/manual acceptance artifact was produced by the recorder or by hand.

## Goals / Non-Goals

**Goals:**

- Add provenance metadata to recorder-generated live/manual acceptance artifacts using the existing `tdx.desktop_trade.pingan_readiness_evidence_artifact.v1` shape.
- Treat live/manual acceptance as complete only when required outcomes are present and the recorder provenance is verified.
- Expose the nested live/manual acceptance provenance status in acceptance coverage and promotion readiness rollup.
- Preserve D-07/D-08 as `[部分实现]` in `FUNCTION_TREE.md`.

**Non-Goals:**

- Do not execute PingAn buy/sell/confirm/submit workflows.
- Do not control the broker desktop, close dialogs, restart processes, or submit orders.
- Do not refresh source evidence, infer operator intent, or convert hand-written artifacts into recorder evidence.
- Do not promote D-07/D-08 to `[已实现]`.

## Decisions

- Use the existing provenance schema with `source_kind=live_manual_acceptance`, `producer=task pingan-live-manual-acceptance`, and `evidence_schema=tdx.desktop_trade.pingan_live_manual_acceptance.v1`. This keeps the recorder artifact aligned with the existing readiness provenance contract instead of creating a parallel schema.
- Keep schema/outcome validation separate from provenance validation. A hand-written artifact can still report valid outcome shape, but it cannot satisfy the implemented-status readiness gate without verified recorder provenance.
- Fail closed in acceptance coverage and rollup. Missing, malformed, mismatched, or unsupported recorder provenance makes `live_manual_acceptance_complete=false`, `acceptance_complete=false`, and adds an explicit rollup block reason.

## Risks / Trade-offs

- Existing hand-authored test fixtures need provenance added when they represent controlled recorder output. This is intentional: fixtures without recorder provenance should now model blocked evidence.
- The live/manual acceptance recorder still records operator assertions; verified provenance proves the artifact was produced through the controlled path, not that a broker production workflow is safe or that FUNCTION_TREE status should change automatically.
