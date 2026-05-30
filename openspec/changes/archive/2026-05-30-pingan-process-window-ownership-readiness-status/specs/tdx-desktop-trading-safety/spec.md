## ADDED Requirements

### Requirement: PingAn passive process/window ownership observation SHALL remain partial lifecycle evidence

PingAn passive process/window ownership observation SHALL count only as read-only lifecycle evidence and SHALL NOT by itself satisfy process ownership, statefile ownership, supervisor, restart/backoff, or live acceptance gates.

#### Scenario: Passive process/window observation is registered without implemented status

- **WHEN** D-07 or D-08 evidence includes `desktop_lifecycle_gate_status.observed_process_window_ownership`
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that the observation does not start, stop, restart, supervise, lock, or otherwise own the PingAn desktop process.
