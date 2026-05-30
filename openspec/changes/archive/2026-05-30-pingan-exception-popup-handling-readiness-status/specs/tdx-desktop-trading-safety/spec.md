## ADDED Requirements

### Requirement: PingAn exception popup handling status SHALL remain partial lifecycle evidence

PingAn exception popup handling status SHALL count only as read-only lifecycle evidence and SHALL NOT by itself satisfy popup close, confirm click, recovery, retry, resubmission, or live acceptance gates.

#### Scenario: Exception popup handling status is registered without implemented status

- **WHEN** D-07 or D-08 evidence includes `desktop_lifecycle_gate_status.exception_popup_handling_status`
- **THEN** the node MUST remain `[部分实现]`
- **AND** the boundary MUST state that the status does not close popups, click controls, recover, retry, resubmit, or provide live/manual acceptance.
