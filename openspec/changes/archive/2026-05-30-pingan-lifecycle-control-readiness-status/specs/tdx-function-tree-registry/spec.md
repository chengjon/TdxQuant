## ADDED Requirements

### Requirement: PingAn lifecycle control status evidence SHALL be registered as partial evidence

`FUNCTION_TREE.md` SHALL register PingAn lifecycle control status as read-only lifecycle evidence without promoting D-07 or D-08 to `[已实现]`.

#### Scenario: Lifecycle control status is registered without status change

- **WHEN** D-07 or D-08 evidence cites `desktop_lifecycle_gate_status.lifecycle_control_status`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the status
- **AND** the boundary SHALL state that executable process lifecycle control, supervisor ownership, PID ownership, restart/backoff, statefile locking, and live/manual acceptance remain required before `[已实现]`.
