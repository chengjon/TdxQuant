## ADDED Requirements

### Requirement: Task preset registry SHALL expose a side-explicit sell submit-once preset

The task preset registry SHALL expose a stable sell-side submit-once preset that targets the existing `trade-submit-once` task workflow without changing submit-once execution behavior.

#### Scenario: Caller resolves the sell submit-once default preset

- **WHEN** a caller resolves `sell-submit-once-default`
- **THEN** the preset MUST target the existing `trade-submit-once` task command
- **AND** it MUST set `side=sell`
- **AND** it MUST continue to require explicit order parameters and existing trade safety controls for real execution
- **AND** it MUST NOT imply a separate sell submit-once desktop primitive exists
