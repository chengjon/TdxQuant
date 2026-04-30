## MODIFIED Requirements

### Requirement: Command catalog CLI SHALL execute named entries through existing preset workflows
The system SHALL allow callers to execute a named catalog entry that resolves to exactly one supported preset in the `task`, `report`, or `trade` command groups.

#### Scenario: Caller requests a summary view for a catalog execution
- **WHEN** a caller executes a catalog run command with summary output enabled
- **THEN** the system MUST return a reduced summary view of the resolved execution result instead of the full detailed result payload

### Requirement: Command catalog CLI SHALL expose a unified daily entry registry
The system SHALL provide a top-level command catalog that lists stable daily entries mapped to existing `task`, `report`, or `trade` preset workflows.

#### Scenario: Caller requests a summary view for a catalog plan
- **WHEN** a caller executes a catalog planning command with summary output enabled
- **THEN** the system MUST return a reduced summary view of the resolved plan instead of the full detailed plan payload
