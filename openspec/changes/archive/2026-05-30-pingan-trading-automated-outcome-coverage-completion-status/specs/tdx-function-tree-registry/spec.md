## ADDED Requirements

### Requirement: PingAn automated outcome coverage completion SHALL be registered as partial evidence

`FUNCTION_TREE.md` SHALL register PingAn automated outcome coverage completion as read-only report evidence without using it to promote D-07 or D-08 to `[已实现]`.

#### Scenario: Automated outcome coverage completion is registered without status change

- **WHEN** D-07 or D-08 evidence cites `acceptance_outcome_coverage_status.automated_outcome_coverage_complete=true`
- **THEN** the node SHALL remain `[部分实现]`
- **AND** the evidence SHALL identify the code and tests that produce the completion flag
- **AND** the boundary SHALL state that live/manual acceptance remains required before `[已实现]`.

