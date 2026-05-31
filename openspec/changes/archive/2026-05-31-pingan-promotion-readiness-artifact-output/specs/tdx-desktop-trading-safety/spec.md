## ADDED Requirements

### Requirement: PingAn promotion readiness artifact output SHALL remain evidence-only

The artifact output path SHALL persist only the already-computed promotion readiness rollup and SHALL NOT execute or refresh any PingAn trading workflow.

#### Scenario: Artifact output stays non-executing

- **WHEN** a caller writes a rollup artifact
- **THEN** the artifact SHALL record `execution_mode=readonly_evidence_rollup`
- **AND** it SHALL record no order submission or control dispatch.

