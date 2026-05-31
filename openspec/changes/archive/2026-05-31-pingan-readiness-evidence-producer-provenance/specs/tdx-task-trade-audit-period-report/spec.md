## ADDED Requirements

### Requirement: Period trade audit report SHALL identify acceptance coverage provenance

`TdxTaskManager.trade_audit_period_report(...)` SHALL include artifact provenance metadata in its acceptance outcome coverage status.

#### Scenario: Period report acceptance coverage carries provenance accepted by promotion readiness rollup

- **WHEN** `TdxTaskManager.trade_audit_period_report(...)` returns `acceptance_outcome_coverage_status`
- **THEN** `acceptance_outcome_coverage_status.artifact_provenance.schema` SHALL be `tdx.desktop_trade.pingan_readiness_evidence_artifact.v1`
- **AND** `acceptance_outcome_coverage_status.artifact_provenance.source_kind` SHALL be `acceptance_coverage`
- **AND** `acceptance_outcome_coverage_status.artifact_provenance.producer` SHALL be `task trade-audit-period-report`
- **AND** `acceptance_outcome_coverage_status.artifact_provenance.evidence_schema` SHALL match `tdx.desktop_trade.pingan_acceptance_outcome_coverage_status.v1`
- **AND** the report SHALL remain read-only and SHALL NOT execute trade workflows.

