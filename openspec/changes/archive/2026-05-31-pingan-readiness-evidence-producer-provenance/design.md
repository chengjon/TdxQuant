# Design

## Overview

The promotion readiness rollup accepts source evidence from three producer classes: preflight, dialog readiness, and acceptance coverage. This change makes those producers self-identifying by adding a shared artifact provenance object:

```json
{
  "schema": "tdx.desktop_trade.pingan_readiness_evidence_artifact.v1",
  "source_kind": "preflight",
  "producer": "trade preflight",
  "evidence_schema": "tdx.desktop_trade.pingan_promotion_gate_status.v1"
}
```

## Producer Mapping

- `trade preflight` emits `source_kind=preflight` and `evidence_schema=tdx.desktop_trade.pingan_promotion_gate_status.v1`.
- `trade dialog-readiness` emits `source_kind=dialog_readiness` and `evidence_schema=tdx.desktop_trade.pingan_desktop_lifecycle_gate_status.v1`.
- `task trade-audit-daily-report` emits `source_kind=acceptance_coverage` and `evidence_schema=tdx.desktop_trade.pingan_acceptance_outcome_coverage_status.v1`.
- `task trade-audit-period-report` emits `source_kind=acceptance_coverage` and `evidence_schema=tdx.desktop_trade.pingan_acceptance_outcome_coverage_status.v1`.

## Placement

For preflight and dialog readiness, provenance is added at the top level of the result `data` payload beside the evidence object. For trade audit reports, provenance is added inside `acceptance_outcome_coverage_status`, because that object is the source evidence consumed by the readiness rollup.

## Boundaries

The change is metadata-only. It does not run broker control, does not submit orders, does not produce live/manual acceptance evidence, and does not change readiness decisions by itself. It only makes existing read-only evidence producer outputs compatible with the existing provenance gate.

