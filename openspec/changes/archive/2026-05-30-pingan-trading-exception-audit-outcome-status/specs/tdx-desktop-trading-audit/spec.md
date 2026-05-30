## MODIFIED Requirements

### Requirement: Finalized PingAn trade workflows SHALL expose audit gate status

The standard finalized PingAn trade persistence path SHALL expose a normalized `trade_audit_gate_status` payload that summarizes the audit evidence written for that finalized result.

#### Scenario: Confirmed finalized trade exposes audit gate status

- **WHEN** a PingAn trade workflow is finalized through the standard artifact-persistence path and writes a confirmed trade-audit artifact
- **THEN** the result data SHALL include `trade_audit_gate_status`
- **AND** that payload SHALL include audit schema, audit id, covered audit status, broker, method, artifact path evidence, `status=partial`, and remaining audit gate statuses.

#### Scenario: Rejected finalized trade exposes audit gate status

- **WHEN** a PingAn trade workflow is rejected before desktop execution and finalized through the same persistence path
- **THEN** the result data SHALL include `trade_audit_gate_status`
- **AND** the covered audit status SHALL be `rejected`
- **AND** the payload SHALL identify which artifact paths were persisted for the rejected result.

#### Scenario: Explicit exception finalized trade exposes audit gate status

- **WHEN** a PingAn trade workflow returns a finalized result with explicit desktop exception metadata
- **THEN** the result data SHALL include `trade_audit_gate_status`
- **AND** the covered audit status SHALL be `exception`
- **AND** the immutable audit artifact SHALL preserve the same `trade_audit.status=exception`.

#### Scenario: Audit gate status remains partial

- **WHEN** `trade_audit_gate_status` is returned for one finalized result
- **THEN** the payload SHALL state that it is partial audit promotion evidence
- **AND** it SHALL list remaining audit gate statuses that still require separate evidence before implemented status.

