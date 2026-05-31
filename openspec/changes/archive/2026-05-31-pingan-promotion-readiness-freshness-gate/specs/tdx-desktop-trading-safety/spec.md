## ADDED Requirements

### Requirement: PingAn promotion readiness freshness gating SHALL remain read-only

The evidence freshness gate SHALL only classify evidence freshness and SHALL NOT execute any PingAn trading workflow or desktop lifecycle action.

#### Scenario: Stale evidence does not trigger workflow execution

- **WHEN** the freshness gate marks evidence stale
- **THEN** it SHALL still remain a read-only classification
- **AND** it SHALL not call broker, desktop, trade, report, or catalog execution paths.

