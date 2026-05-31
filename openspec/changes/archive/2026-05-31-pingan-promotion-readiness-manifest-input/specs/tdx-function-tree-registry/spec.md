## ADDED Requirements

### Requirement: FUNCTION_TREE SHALL register promotion readiness manifest input without status promotion

FUNCTION_TREE SHALL record the evidence manifest input as a reproducibility aid for D-07/D-08 while preserving `[部分实现]` status.

#### Scenario: Manifest input is registered as read-only evidence selection

- **WHEN** the manifest input is added to D-07/D-08
- **THEN** the tree SHALL include the manifest path option and manifest metadata
- **AND** the boundary SHALL state that manifests do not refresh evidence or execute workflows
- **AND** D-07/D-08 SHALL remain `[部分实现]`.

