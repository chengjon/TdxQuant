## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn process lifecycle control without over-promotion

`FUNCTION_TREE.md` SHALL register PingAn process lifecycle control evidence on D-07 and D-08 while preserving accurate partial status.

#### Scenario: D-07 and D-08 register process lifecycle evidence

- **WHEN** PingAn process lifecycle manager and CLI entrypoints are added
- **THEN** D-07 and D-08 MUST include evidence for `pingan-process-lifecycle-control`
- **AND** D-07 and D-08 MUST include evidence for `TdxTradeManager.pingan.lifecycle_process`
- **AND** D-07 and D-08 MUST include evidence for `trade lifecycle-process`
- **AND** D-07 and D-08 MUST remain `[部分实现]` unless all remaining live/manual acceptance and trading readiness gates are independently satisfied.

#### Scenario: FUNCTION_TREE boundary prevents readiness overclaiming

- **WHEN** D-07 or D-08 mention process lifecycle control evidence
- **THEN** the boundary MUST state that this controls only explicit owner-locked local process start/stop/restart for recorded PIDs
- **AND** the boundary MUST state that it does not submit orders, execute catalog/task/report/bundle workflows, prove broker readiness, prove UI login readiness, or provide production trading readiness.
