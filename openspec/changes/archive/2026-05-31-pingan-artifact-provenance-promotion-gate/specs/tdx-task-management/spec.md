## ADDED Requirements

### Requirement: PingAn promotion readiness SHALL require artifact provenance for implemented-status review

`TdxTaskManager.pingan_promotion_readiness_rollup` SHALL verify artifact provenance metadata for each source evidence file before the implemented-status promotion decision can become eligible for review.

#### Scenario: Valid artifact provenance satisfies provenance gate

- **GIVEN** each source evidence file contains `artifact_provenance.schema=tdx.desktop_trade.pingan_readiness_evidence_artifact.v1`
- **AND** each provenance object carries the matching source kind, expected evidence schema, and allowed producer
- **WHEN** the rollup builds `artifact_provenance_status`
- **THEN** `artifact_provenance_status.status` SHALL be `verified`
- **AND** `artifact_provenance_status.invalid_source_kinds` SHALL be empty.

#### Scenario: Schema-valid but provenance-less evidence is blocked

- **GIVEN** source evidence contains complete gates and valid producer schemas
- **BUT** one or more source files do not contain valid `artifact_provenance`
- **WHEN** the rollup builds `implemented_status_promotion_decision`
- **THEN** `artifact_provenance_status.status` SHALL be `unverified`
- **AND** `implemented_status_promotion_decision.decision` SHALL be `blocked`
- **AND** `implemented_status_promotion_decision.blocked_reasons` SHALL include `unverified_artifact_provenance`.

#### Scenario: Provenance mismatch is reported per source kind

- **GIVEN** a source evidence file has an artifact provenance object with mismatched source kind, evidence schema, or unsupported producer
- **WHEN** the rollup builds `artifact_provenance_status`
- **THEN** the source kind SHALL be listed in `artifact_provenance_status.invalid_source_kinds`
- **AND** the source status SHALL expose a reason for the mismatch.
