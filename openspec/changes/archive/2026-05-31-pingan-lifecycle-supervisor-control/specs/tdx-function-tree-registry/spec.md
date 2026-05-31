## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn lifecycle supervisor control without over-promotion

`FUNCTION_TREE.md` SHALL register PingAn lifecycle supervisor control evidence on D-07 and D-08 while preserving accurate feature status.

#### Scenario: D-07 and D-08 register supervisor evidence as partial lifecycle control

- **WHEN** PingAn lifecycle supervisor tick/run manager methods and CLI entrypoints are added
- **THEN** D-07 and D-08 MUST include evidence for `pingan-lifecycle-supervisor-control`
- **AND** D-07 and D-08 MUST include evidence for `TdxTradeManager.pingan.lifecycle_supervisor_tick`
- **AND** D-07 and D-08 MUST include evidence for `trade lifecycle-supervisor-tick`
- **AND** D-07 and D-08 MUST remain `[部分实现]` unless all remaining live/manual acceptance and desktop lifecycle gates are independently satisfied.

#### Scenario: FUNCTION_TREE boundary prevents lifecycle readiness overclaiming

- **WHEN** D-07 or D-08 mention lifecycle supervisor evidence
- **THEN** the boundary MUST state that the evidence is local statefile-backed lifecycle control
- **AND** the boundary MUST state that it does not submit orders, execute catalog/task/report/bundle workflows, own/kill/start the real PingAn process, or prove production trading readiness.
