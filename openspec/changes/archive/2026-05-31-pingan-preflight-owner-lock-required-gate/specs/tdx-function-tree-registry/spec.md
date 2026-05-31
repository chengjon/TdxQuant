## ADDED Requirements

### Requirement: PingAn required owner lock preflight gate evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite PingAn required owner lock preflight gate evidence as partial safety/lifecycle evidence while preserving D-07/D-08 partial status.

#### Scenario: Required owner lock preflight gate is registered without status change

- **WHEN** D-07 or D-08 evidence cites `lifecycle_owner_lock_status.required=true`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce the required owner lock preflight gate
- **AND** the boundary SHALL state that the gate is read-only local statefile safety evidence and does not provide real process lifecycle control, broker readiness, or live/manual acceptance.
