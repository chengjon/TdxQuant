## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn process lifecycle controller boundary without over-promotion

`FUNCTION_TREE.md` SHALL register PingAn process lifecycle controller-boundary evidence while preserving accurate feature status and explicit boundaries.

#### Scenario: D-12 registers process lifecycle controller boundary evidence

- **WHEN** PingAn process lifecycle owner-gate and recorded-PID guard decisions are routed through `PingAnLifecycleController`
- **THEN** `FUNCTION_TREE.md` MUST cite the controller code, manager routing, tests, and this OpenSpec change as evidence
- **AND** the boundary MUST state that the controller is pure decision/result assembly and does not execute process spawn, process kill, statefile writes, desktop automation, or order submission.

#### Scenario: D-07 and D-08 remain bounded trading features

- **WHEN** process lifecycle controller-boundary evidence is registered
- **THEN** D-07 and D-08 MUST NOT be promoted solely from architecture boundary extraction
- **AND** their boundaries MUST continue to distinguish lifecycle governance evidence from broker readiness, order acceptance, production readiness, and full trading workflow completion.
