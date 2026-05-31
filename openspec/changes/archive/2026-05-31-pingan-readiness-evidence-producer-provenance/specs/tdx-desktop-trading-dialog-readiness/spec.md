## ADDED Requirements

### Requirement: PingAn dialog readiness SHALL identify lifecycle evidence provenance

`TdxTradeManager.pingan.dialog_readiness(...)` SHALL include artifact provenance metadata for the desktop lifecycle gate status evidence it returns.

#### Scenario: Dialog readiness output carries provenance accepted by promotion readiness rollup

- **WHEN** `TdxTradeManager.pingan.dialog_readiness(...)` returns a `desktop_lifecycle_gate_status`
- **THEN** result data SHALL include `artifact_provenance`
- **AND** `artifact_provenance.schema` SHALL be `tdx.desktop_trade.pingan_readiness_evidence_artifact.v1`
- **AND** `artifact_provenance.source_kind` SHALL be `dialog_readiness`
- **AND** `artifact_provenance.producer` SHALL be `trade dialog-readiness`
- **AND** `artifact_provenance.evidence_schema` SHALL match `tdx.desktop_trade.pingan_desktop_lifecycle_gate_status.v1`
- **AND** dialog readiness SHALL remain read-only and SHALL NOT submit orders or dispatch control actions.

