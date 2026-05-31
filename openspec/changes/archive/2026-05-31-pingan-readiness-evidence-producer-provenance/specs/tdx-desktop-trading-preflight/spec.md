## ADDED Requirements

### Requirement: PingAn preflight SHALL identify readiness evidence provenance

`TdxTradeManager.pingan.preflight(...)` SHALL include artifact provenance metadata for the promotion gate status evidence it returns.

#### Scenario: Preflight output carries provenance accepted by promotion readiness rollup

- **WHEN** `TdxTradeManager.pingan.preflight(...)` returns a `promotion_gate_status`
- **THEN** result data SHALL include `artifact_provenance`
- **AND** `artifact_provenance.schema` SHALL be `tdx.desktop_trade.pingan_readiness_evidence_artifact.v1`
- **AND** `artifact_provenance.source_kind` SHALL be `preflight`
- **AND** `artifact_provenance.producer` SHALL be `trade preflight`
- **AND** `artifact_provenance.evidence_schema` SHALL match `tdx.desktop_trade.pingan_promotion_gate_status.v1`
- **AND** the preflight workflow SHALL remain read-only and SHALL NOT submit orders.

