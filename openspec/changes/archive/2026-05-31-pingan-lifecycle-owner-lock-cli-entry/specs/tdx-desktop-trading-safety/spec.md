## ADDED Requirements

### Requirement: PingAn lifecycle owner lock CLI SHALL remain partial lifecycle evidence

The PingAn lifecycle owner lock CLI entry SHALL be treated as explicit local statefile control and SHALL NOT be treated as proof of live trading readiness.

#### Scenario: Lifecycle owner lock CLI is registered without implemented trading status

- **WHEN** D-07 or D-08 evidence includes the `trade lifecycle-owner-lock` CLI entry
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that the CLI writes only local owner lock state when requested and does not start, stop, restart, kill, supervise, back off, submit orders, claim real desktop PID ownership, or provide live/manual acceptance.
