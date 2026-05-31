## ADDED Requirements

### Requirement: PingAn process lifecycle control SHALL remain bounded desktop lifecycle evidence

PingAn process lifecycle control SHALL be explicit operator-owned process lifecycle evidence and MUST NOT imply broker readiness, order readiness, or live/manual trading acceptance.

#### Scenario: Process lifecycle evidence keeps boundaries explicit

- **WHEN** PingAn process lifecycle control returns status/start/stop/restart evidence
- **THEN** the evidence MUST include `execution_mode=explicit_operator_process_lifecycle_control`
- **AND** mutating actions MUST report `side_effect_level=local_lifecycle_statefile_and_process`
- **AND** the evidence MUST include `order_submitted=false`
- **AND** the evidence MUST state that only a recorded PID owned by the lifecycle statefile can be stopped or restarted
- **AND** the evidence MUST state that broker readiness, UI login readiness, workflow execution, and live/manual acceptance remain out of scope.
