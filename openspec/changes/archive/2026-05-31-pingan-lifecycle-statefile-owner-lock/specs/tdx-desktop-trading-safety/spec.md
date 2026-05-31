## ADDED Requirements

### Requirement: PingAn lifecycle owner lock SHALL remain statefile-only lifecycle evidence

The PingAn lifecycle owner lock surface SHALL be treated as a local ownership artifact, not as proof of executable desktop lifecycle control or live trading readiness.

#### Scenario: Lifecycle owner lock does not control desktop process

- **WHEN** PingAn lifecycle owner lock status, acquire, or release returns a payload
- **THEN** the payload MUST state that no order was submitted and no desktop control dispatch was executed
- **AND** the payload MUST state that start, stop, restart, kill, supervisor ownership, backoff execution, PID ownership, event-log writes, submission-ledger writes, and trade-audit writes were not performed.

#### Scenario: Lifecycle owner lock is registered without implemented trading status

- **WHEN** D-07 or D-08 evidence includes PingAn lifecycle owner lock acquire/release behavior
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that real process lifecycle control, supervisor ownership, restart/backoff, live provider readiness, and live/manual acceptance remain required before `[已实现]`.
