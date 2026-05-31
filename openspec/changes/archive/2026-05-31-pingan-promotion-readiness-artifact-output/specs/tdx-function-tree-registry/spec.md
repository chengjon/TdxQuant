## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register promotion readiness artifact output without status promotion

FUNCTION_TREE SHALL record the JSON artifact output as evidence capture for D-07/D-08 and SHALL keep those nodes `[部分实现]`.

#### Scenario: Artifact output is registered as evidence-only

- **WHEN** the artifact output is added to D-07/D-08
- **THEN** the tree SHALL include the task option and output metadata
- **AND** the boundary SHALL state that artifact writing does not refresh evidence or execute workflows
- **AND** D-07/D-08 SHALL remain `[部分实现]`.

