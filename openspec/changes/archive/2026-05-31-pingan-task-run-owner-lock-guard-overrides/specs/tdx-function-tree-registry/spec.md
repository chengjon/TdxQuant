## ADDED Requirements

### Requirement: PingAn task-run owner-lock guard evidence SHALL be registered as partial evidence

The FUNCTION_TREE registry SHALL cite task-run preset/override owner-lock guard forwarding as partial D-07/D-08 safety evidence only.

#### Scenario: Task-run guard evidence is registered without status change

- **WHEN** D-07 or D-08 evidence cites `task run` owner-lock guard preset/override forwarding
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code, tests, and OpenSpec change that produce task-run guard forwarding
- **AND** the boundary SHALL state that the task-run layer only resolves and forwards an opt-in local guard and does not acquire/release locks, write lifecycle statefile/lock artifacts directly, control PingAn processes, prove broker readiness, or provide live/manual acceptance.
