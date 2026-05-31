## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn supervisor process restart integration without over-promotion

`FUNCTION_TREE.md` SHALL register PingAn supervisor process restart integration evidence on D-07 and D-08 while preserving accurate partial status.

#### Scenario: D-07 and D-08 register supervisor process restart evidence

- **WHEN** supervisor tick/run can opt into recorded-PID process restart
- **THEN** D-07 and D-08 MUST include evidence for `pingan-supervisor-process-restart-control`
- **AND** D-07 and D-08 MUST include evidence for `process_restart_enabled`
- **AND** D-07 and D-08 MUST include evidence for `trade lifecycle-supervisor-tick --process-restart`
- **AND** D-07 and D-08 MUST remain `[部分实现]`.

#### Scenario: FUNCTION_TREE boundary prevents supervisor restart overclaiming

- **WHEN** D-07 or D-08 mention supervisor process restart evidence
- **THEN** the boundary MUST state that process restart is explicit opt-in and delegated to recorded-PID lifecycle process guards
- **AND** the boundary MUST state that it does not submit orders, execute catalog/task/report/bundle workflows, prove broker readiness, prove UI login readiness, or provide production trading readiness.
