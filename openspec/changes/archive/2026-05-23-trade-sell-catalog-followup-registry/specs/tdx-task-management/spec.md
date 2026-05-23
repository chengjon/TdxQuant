## ADDED Requirements

### Requirement: Task preset registry SHALL expose a stable trade-sell default preset

The task preset registry SHALL expose a stable preset for the existing `trade-sell` task workflow without changing sell execution behavior.

#### Scenario: Caller resolves the task sell default preset

- **WHEN** a caller resolves `task-sell-default`
- **THEN** the preset MUST target the existing `trade-sell` task command
- **AND** it MUST use the existing `trade_sell` task profile
- **AND** real sell execution MUST continue to require explicit order parameters and existing trade safety controls
