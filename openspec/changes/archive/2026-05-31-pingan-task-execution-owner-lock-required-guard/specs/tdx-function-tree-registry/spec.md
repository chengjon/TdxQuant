## ADDED Requirements

### Requirement: PingAn task execution owner-lock guard evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite task-level PingAn owner-lock execution guard coverage as partial safety/lifecycle evidence while preserving D-07/D-08 partial status.

#### Scenario: Task owner-lock guard evidence is registered without status change

- **WHEN** D-07 or D-08 evidence cites task trade owner-lock guard forwarding
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce task-level owner-lock guard forwarding
- **AND** the boundary SHALL state that the task layer only forwards an opt-in local guard and does not acquire/release locks, write lifecycle statefile/lock artifacts directly, control PingAn processes, prove broker readiness, or provide live/manual acceptance.
