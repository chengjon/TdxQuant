## ADDED Requirements

### Requirement: PingAn preflight owner lock status evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite PingAn preflight lifecycle owner lock status as partial lifecycle evidence while preserving D-07/D-08 partial status.

#### Scenario: Preflight owner lock status evidence is registered without status change

- **WHEN** D-07 or D-08 evidence cites `promotion_gate_status.lifecycle_owner_lock_status`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce the preflight owner lock status gate
- **AND** the boundary SHALL state that preflight owner lock status is read-only local statefile evidence and does not provide real process lifecycle control, broker readiness, or live/manual acceptance.
