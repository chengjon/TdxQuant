# PingAn Evidence Provenance Promotion Gate

## Why

The current PingAn implemented-status promotion decision is fail-closed for missing, stale, sample, and incomplete evidence, but it still trusts any JSON object that contains the expected gate names. That is too weak for D-07/D-08 mainline completion because hand-written JSON can look complete without proving it came from the supported PingAn preflight, dialog readiness, and acceptance coverage producers.

The next correction is to require source evidence provenance at the schema-contract level before an evidence package can become `eligible_for_review`.

## What Changes

- Add an evidence contract status to PingAn promotion readiness rollup.
- Verify each source evidence kind against the expected producer schema:
  - preflight: `tdx.desktop_trade.pingan_promotion_gate_status.v1`
  - dialog readiness: `tdx.desktop_trade.pingan_desktop_lifecycle_gate_status.v1`
  - acceptance coverage: `tdx.desktop_trade.pingan_acceptance_outcome_coverage_status.v1`
- Block implemented-status review when evidence is missing, schema-less, or schema-mismatched.
- Preserve all existing non-execution boundaries.
- Register the provenance gate in `FUNCTION_TREE.md` while keeping D-07/D-08 `[部分实现]`.

## Non-Goals

- Do not execute PingAn workflows.
- Do not produce live evidence automatically.
- Do not claim production readiness from schema validation.
- Do not auto-edit `FUNCTION_TREE.md` status.
- Do not promote D-07 or D-08 to `[已实现]`.
