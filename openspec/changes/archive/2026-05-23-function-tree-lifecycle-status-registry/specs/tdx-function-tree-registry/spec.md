## ADDED Requirements

### Requirement: FUNCTION_TREE lifecycle material status SHALL be explicitly bounded

The FUNCTION_TREE registry SHALL allow the OpenSpec lifecycle material node to be marked implemented when the registry validator, evidence checks, tests, and machine-readable report are present, provided the node boundary clearly states that the validator does not prove downstream feature runtime availability.

#### Scenario: Lifecycle material node is implemented with validation evidence

- **WHEN** the lifecycle material node cites the validator script, validator tests, OpenSpec evidence checks, local evidence path checks, ROADMAP rejection, and JSON report output
- **THEN** the node MAY be registered as `[已实现]`
- **AND** the boundary MUST state that the validator does not execute evidence paths or prove cited feature availability

#### Scenario: Lifecycle status does not affect downstream feature status

- **WHEN** the lifecycle material node is registered as `[已实现]`
- **THEN** other feature nodes MUST retain their own explicit status, evidence, and boundary
