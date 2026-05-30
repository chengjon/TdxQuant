## ADDED Requirements

### Requirement: PingAn lifecycle control status SHALL remain partial lifecycle evidence

PingAn lifecycle control status SHALL count only as read-only lifecycle evidence and SHALL NOT by itself satisfy process lifecycle ownership, supervisor ownership, restart/backoff, statefile ownership, or live acceptance gates.

#### Scenario: Lifecycle control status is registered without implemented status

- **WHEN** D-07 or D-08 evidence includes `desktop_lifecycle_gate_status.lifecycle_control_status`
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that the status does not start, stop, restart, kill, supervise, back off, claim PID ownership, write state/ledger/audit artifacts, or provide live/manual acceptance.
