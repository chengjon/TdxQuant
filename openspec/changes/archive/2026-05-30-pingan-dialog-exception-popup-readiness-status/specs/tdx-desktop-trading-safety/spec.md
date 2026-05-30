## ADDED Requirements

### Requirement: PingAn passive exception popup lookup SHALL remain partial lifecycle evidence

PingAn passive exception popup lookup SHALL count only as read-only lifecycle evidence and SHALL NOT by itself satisfy exception popup handling, retry, recovery, or live acceptance gates.

#### Scenario: Passive exception popup lookup is registered without implemented status

- **WHEN** D-07 or D-08 evidence includes `desktop_lifecycle_gate_status.dialog_checks.exception_popup_lookup`
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that the lookup does not close popups, retry orders, recover state, prove broker readiness, or provide live/manual acceptance.

