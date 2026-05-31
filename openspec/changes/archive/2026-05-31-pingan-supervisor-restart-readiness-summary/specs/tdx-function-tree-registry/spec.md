## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register PingAn post-restart readiness summary without over-promotion

`FUNCTION_TREE.md` SHALL register PingAn supervisor post-restart readiness summary evidence on D-07 and D-08 while preserving accurate partial status.

#### Scenario: D-07 and D-08 register post-restart summary evidence

- **WHEN** supervisor tick/run can opt into post-restart broker health recheck
- **THEN** D-07 and D-08 MUST include evidence for `pingan-supervisor-restart-readiness-summary`
- **AND** D-07 and D-08 MUST include evidence for `process_restart_recheck_enabled`
- **AND** D-07 and D-08 MUST include evidence for `lifecycle_recovery_status`
- **AND** D-07 and D-08 MUST remain `[部分实现]`.

#### Scenario: FUNCTION_TREE boundary prevents readiness overclaiming

- **WHEN** D-07 or D-08 mention post-restart readiness summary evidence
- **THEN** the boundary MUST state that post-restart health recheck is immediate lifecycle evidence only
- **AND** the boundary MUST state that it does not prove order readiness, UI login readiness, broker production readiness, or live/manual acceptance.
