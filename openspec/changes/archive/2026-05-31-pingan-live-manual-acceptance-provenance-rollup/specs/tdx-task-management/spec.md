## ADDED Requirements

### Requirement: PingAn live/manual acceptance artifacts SHALL carry recorder provenance

`TdxTaskManager.pingan_live_manual_acceptance(...)` SHALL include readiness evidence artifact provenance in generated live/manual acceptance artifacts so downstream readiness gates can distinguish controlled recorder output from hand-written JSON.

#### Scenario: Recorder writes provenance metadata

- **WHEN** the recorder writes a `tdx.desktop_trade.pingan_live_manual_acceptance.v1` artifact
- **THEN** the artifact SHALL contain `artifact_provenance.schema=tdx.desktop_trade.pingan_readiness_evidence_artifact.v1`
- **AND** `artifact_provenance.source_kind` SHALL be `live_manual_acceptance`
- **AND** `artifact_provenance.producer` SHALL be `task pingan-live-manual-acceptance`
- **AND** `artifact_provenance.evidence_schema` SHALL be `tdx.desktop_trade.pingan_live_manual_acceptance.v1`.

### Requirement: PingAn acceptance coverage SHALL require verified live/manual recorder provenance

The acceptance coverage status SHALL treat live/manual acceptance as complete only when the artifact has valid outcome coverage and verified recorder provenance.

#### Scenario: Provenance-less manual acceptance artifact remains incomplete

- **GIVEN** a live/manual acceptance artifact has the expected schema and all required accepted outcomes
- **BUT** it lacks valid `artifact_provenance`
- **WHEN** acceptance coverage evaluates the artifact
- **THEN** `live_manual_acceptance.status` SHALL report `incomplete`
- **AND** `live_manual_acceptance.artifact_provenance_status.status` SHALL report `unverified`
- **AND** `live_manual_acceptance_complete` SHALL be false
- **AND** `acceptance_complete` SHALL be false.

#### Scenario: Recorder-produced manual acceptance artifact completes the gate

- **GIVEN** a live/manual acceptance artifact has the expected schema, all required accepted outcomes, and verified recorder provenance
- **WHEN** acceptance coverage evaluates the artifact
- **THEN** `live_manual_acceptance.status` SHALL report `complete`
- **AND** `live_manual_acceptance.artifact_provenance_status.status` SHALL report `verified`
- **AND** `live_manual_acceptance_complete` SHALL be true when automated outcome coverage is complete.

### Requirement: PingAn promotion readiness rollup SHALL surface live/manual recorder provenance

`TdxTaskManager.pingan_promotion_readiness_rollup(...)` SHALL include live/manual acceptance recorder provenance status in its read-only rollup and block implemented-status review when the nested recorder provenance is missing or unverified.

#### Scenario: Rollup blocks unverified live/manual recorder provenance

- **GIVEN** preflight, dialog readiness, and acceptance coverage evidence otherwise report complete gates
- **BUT** the nested live/manual acceptance artifact provenance is missing or unverified
- **WHEN** the promotion readiness rollup is built
- **THEN** `live_manual_acceptance_provenance_status.status` SHALL be `unverified`
- **AND** `gate_statuses.live_manual_acceptance.complete` SHALL be false
- **AND** `implemented_status_promotion_decision.blocked_reasons` SHALL include `unverified_live_manual_acceptance_artifact_provenance`
- **AND** the rollup SHALL remain read-only with no order submission and no FUNCTION_TREE status transition.
