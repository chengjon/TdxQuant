# Design

## Artifact Provenance Object

Each source evidence JSON may include:

```json
{
  "artifact_provenance": {
    "schema": "tdx.desktop_trade.pingan_readiness_evidence_artifact.v1",
    "source_kind": "preflight",
    "producer": "trade preflight",
    "evidence_schema": "tdx.desktop_trade.pingan_promotion_gate_status.v1"
  }
}
```

Required source kinds:

- `preflight`
- `dialog_readiness`
- `acceptance_coverage`

## Validation Rules

`artifact_provenance_status` is `verified` only when every source has:

- `artifact_provenance.schema=tdx.desktop_trade.pingan_readiness_evidence_artifact.v1`
- matching `source_kind`
- matching `evidence_schema`
- allowed `producer` for that source kind

Allowed producer names:

- preflight: `trade preflight`, `TdxTradeManager.pingan.preflight`
- dialog readiness: `trade dialog-readiness`, `TdxTradeManager.pingan.dialog_readiness`
- acceptance coverage: `task trade-audit-daily-report`, `task trade-audit-period-report`, `TdxTaskManager.trade_audit_daily_report`, `TdxTaskManager.trade_audit_period_report`

## Promotion Decision Integration

If `artifact_provenance_status.status != verified`, `implemented_status_promotion_decision.blocked_reasons` includes `unverified_artifact_provenance`.

This means schema-valid ad hoc JSON can pass schema-contract validation but still cannot enter D-07/D-08 implemented-status review.

## Boundary

The gate validates metadata only. It does not prove live broker availability, UI login readiness, order safety, manual acceptance authenticity, or production readiness by itself.
