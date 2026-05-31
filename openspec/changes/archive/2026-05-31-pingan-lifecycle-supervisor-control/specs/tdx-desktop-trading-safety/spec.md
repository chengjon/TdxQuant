## ADDED Requirements

### Requirement: PingAn lifecycle supervisor control SHALL remain bounded lifecycle evidence

PingAn lifecycle supervisor control SHALL remain local, operator-owned lifecycle evidence and MUST NOT imply live/manual trading acceptance or production readiness.

#### Scenario: Supervisor control evidence keeps execution boundaries explicit

- **WHEN** supervisor tick or run returns lifecycle evidence
- **THEN** the evidence MUST include `execution_mode=explicit_operator_lifecycle_supervisor_control`
- **AND** the evidence MUST include `side_effect_level=local_lifecycle_statefile` only when it writes the lifecycle statefile
- **AND** the evidence MUST include `order_submitted=false`
- **AND** the evidence MUST include `process_kill_executed=false`
- **AND** the evidence MUST include `pid_ownership_claimed=false`
- **AND** the evidence MUST include a boundary explaining that this slice records local lifecycle restart/backoff decisions and does not execute trading workflows or own the real PingAn desktop process.
