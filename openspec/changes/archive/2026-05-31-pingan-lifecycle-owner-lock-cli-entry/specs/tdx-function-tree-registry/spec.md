## ADDED Requirements

### Requirement: PingAn lifecycle owner lock CLI evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite the PingAn lifecycle owner lock CLI entry as partial lifecycle evidence while preserving D-07/D-08 partial status.

#### Scenario: Lifecycle owner lock CLI evidence is registered without status change

- **WHEN** D-07 or D-08 evidence cites `trade lifecycle-owner-lock`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce the CLI entry
- **AND** the boundary SHALL state that CLI access to owner lock statefiles does not provide real process lifecycle control, broker readiness, or live/manual acceptance.
