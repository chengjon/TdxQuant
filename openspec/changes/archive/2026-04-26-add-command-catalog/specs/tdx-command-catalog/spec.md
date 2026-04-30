## ADDED Requirements

### Requirement: Command catalog CLI SHALL expose a unified daily entry registry
The system SHALL provide a top-level command catalog that lists stable daily entries mapped to existing `task`, `report`, or `trade` preset workflows.

#### Scenario: Caller lists available catalog entries
- **WHEN** a caller executes the catalog listing command
- **THEN** the system MUST return the available entry names together with their mapped source, preset, and resolved command metadata

### Requirement: Command catalog CLI SHALL execute named entries through existing preset workflows
The system SHALL allow callers to execute a named catalog entry that resolves to exactly one supported preset in the `task`, `report`, or `trade` command groups.

#### Scenario: Caller runs a trade-backed catalog entry
- **WHEN** a caller executes a catalog entry whose source is `trade`
- **THEN** the system MUST dispatch execution through the existing trade preset execution path rather than a duplicated workflow

#### Scenario: Caller runs a report-backed catalog entry
- **WHEN** a caller executes a catalog entry whose source is `report`
- **THEN** the system MUST dispatch execution through the existing report preset execution path rather than a duplicated workflow

#### Scenario: Caller runs a task-backed catalog entry
- **WHEN** a caller executes a catalog entry whose source is `task`
- **THEN** the system MUST dispatch execution through the existing task preset execution path rather than a duplicated workflow

#### Scenario: Explicit CLI arguments override downstream preset defaults
- **WHEN** a caller executes a named catalog entry and also provides overlapping CLI arguments explicitly
- **THEN** the system MUST prefer the explicit CLI argument values over the downstream preset defaults

#### Scenario: Catalog entry points to an unsupported source
- **WHEN** a caller executes a catalog entry whose configured source is not one of `task`, `report`, or `trade`
- **THEN** the system MUST reject the request with an invalid-request style error instead of dispatching an unknown workflow
