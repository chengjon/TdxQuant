## ADDED Requirements

### Requirement: PingAn promotion readiness SHALL require source evidence schema contracts for implemented-status review

`TdxTaskManager.pingan_promotion_readiness_rollup` SHALL verify the provenance contract of each source evidence artifact before the implemented-status promotion decision can become eligible for review.

#### Scenario: Valid producer schemas satisfy the evidence contract

- **GIVEN** preflight evidence includes `promotion_gate_status.schema_version=tdx.desktop_trade.pingan_promotion_gate_status.v1`
- **AND** dialog readiness evidence includes `desktop_lifecycle_gate_status.schema_version=tdx.desktop_trade.pingan_desktop_lifecycle_gate_status.v1`
- **AND** acceptance coverage evidence includes `acceptance_outcome_coverage_status.schema=tdx.desktop_trade.pingan_acceptance_outcome_coverage_status.v1`
- **WHEN** the rollup builds `evidence_contract_status`
- **THEN** `evidence_contract_status.status` SHALL be `verified`
- **AND** `evidence_contract_status.invalid_source_kinds` SHALL be empty.

#### Scenario: Complete-looking schema-less evidence is not eligible for implemented-status review

- **GIVEN** source evidence contains complete-looking gate fields
- **BUT** one or more source evidence objects do not carry the expected producer schema
- **WHEN** the rollup builds `implemented_status_promotion_decision`
- **THEN** `evidence_contract_status.status` SHALL be `unverified`
- **AND** `implemented_status_promotion_decision.decision` SHALL be `blocked`
- **AND** `implemented_status_promotion_decision.blocked_reasons` SHALL include `unverified_evidence_contract`.

#### Scenario: Schema mismatch blocks implemented-status review

- **GIVEN** a source evidence object carries a schema key that does not match the expected producer schema
- **WHEN** the rollup builds `implemented_status_promotion_decision`
- **THEN** the corresponding source kind SHALL be listed in `evidence_contract_status.invalid_source_kinds`
- **AND** `blocked_reasons` SHALL include `unverified_evidence_contract`.
