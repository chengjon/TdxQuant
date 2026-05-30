## ADDED Requirements

### Requirement: PingAn process/window observation evidence SHALL be registered as partial evidence

`FUNCTION_TREE.md` SHALL register PingAn process/window observation as read-only lifecycle evidence without promoting D-07 or D-08 to `[已实现]`.

#### Scenario: Process/window observation is registered without status change

- **WHEN** D-07 or D-08 evidence cites `desktop_lifecycle_gate_status.observed_process_window_ownership`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the observation status
- **AND** the boundary SHALL state that real lifecycle control, process ownership, statefile locking, restart/backoff, and live/manual acceptance remain required before `[已实现]`.
