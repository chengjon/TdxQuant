## ADDED Requirements

### Requirement: PingAn exception popup readiness evidence SHALL be registered as partial evidence

`FUNCTION_TREE.md` SHALL register PingAn exception popup readiness as read-only lifecycle evidence without promoting D-07 or D-08 to `[已实现]`.

#### Scenario: Exception popup readiness is registered without status change

- **WHEN** D-07 or D-08 evidence cites `desktop_lifecycle_gate_status.dialog_checks.exception_popup_lookup`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the lookup status
- **AND** the boundary SHALL state that actual exception popup handling, retry/recovery, and live/manual acceptance remain required before `[已实现]`.

