## MODIFIED Requirements

### Requirement: Command catalog CLI SHALL expose a unified daily entry registry
The system SHALL provide a top-level command catalog that lists stable daily entries mapped to existing `task`, `report`, or `trade` preset workflows.

#### Scenario: Caller lists available catalog entries
- **WHEN** a caller executes the catalog listing command
- **THEN** the system MUST return the available entry names together with their mapped source, preset, and resolved command metadata

#### Scenario: Caller filters catalog entries by label
- **WHEN** a caller executes the catalog listing command with a label filter
- **THEN** the system MUST return only entries whose configured labels include that label

### Requirement: Command catalog CLI SHALL support named multi-step bundles composed from existing catalog entries
The system SHALL allow callers to define a named bundle that references multiple existing catalog entries and executes them sequentially through the existing single-entry dispatch path.

#### Scenario: Caller lists available catalog bundles
- **WHEN** a caller executes the catalog listing command for bundles
- **THEN** the system MUST return the available bundle names together with their resolved step metadata

#### Scenario: Caller filters catalog bundles by label
- **WHEN** a caller executes the catalog listing command for bundles with a label filter
- **THEN** the system MUST return only bundles whose configured labels include that label
