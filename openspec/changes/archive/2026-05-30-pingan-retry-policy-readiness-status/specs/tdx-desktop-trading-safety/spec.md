## ADDED Requirements

### Requirement: PingAn retry policy status SHALL remain partial lifecycle evidence

PingAn retry policy status SHALL count only as read-only lifecycle evidence and SHALL NOT by itself satisfy retry, backoff, recovery, resubmission, or live acceptance gates.

#### Scenario: Retry policy status is registered without implemented status

- **WHEN** D-07 or D-08 evidence includes `desktop_lifecycle_gate_status.retry_policy_status`
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that the status does not retry, back off, recover, resubmit, or provide live/manual acceptance.
