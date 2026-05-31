## ADDED Requirements

### Requirement: PingAn lifecycle owner lock evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite PingAn lifecycle owner lock evidence as a concrete local lifecycle artifact while preserving D-07/D-08 partial status.

#### Scenario: Lifecycle owner lock evidence is registered without status change

- **WHEN** D-07 or D-08 evidence cites PingAn lifecycle owner lock acquire/release behavior
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce the owner lock behavior
- **AND** the boundary SHALL state that executable process lifecycle control, supervisor ownership, PID ownership, restart/backoff, broker readiness, and live/manual acceptance remain required before `[已实现]`.
