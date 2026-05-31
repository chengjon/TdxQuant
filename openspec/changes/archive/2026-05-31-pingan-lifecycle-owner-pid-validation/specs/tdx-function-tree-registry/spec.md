## ADDED Requirements

### Requirement: PingAn owner PID validation evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite PingAn owner PID validation evidence as local lifecycle ownership diagnostics while preserving D-07/D-08 partial status.

#### Scenario: Owner PID validation evidence is registered without status change

- **WHEN** D-07 or D-08 evidence cites PingAn lifecycle owner PID validation
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce the owner PID validation
- **AND** the boundary SHALL state that owner PID liveness does not claim real PingAn desktop process ownership, supervisor control, restart/backoff, broker readiness, or live/manual acceptance.
