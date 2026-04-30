## MODIFIED Requirements

### Requirement: Command catalog CLI SHALL expose a unified daily entry registry
The system SHALL provide a top-level command catalog that lists stable daily entries mapped to existing `task`, `report`, or `trade` preset workflows.

#### Scenario: Caller lists available catalog entries
- **WHEN** a caller executes the catalog listing command
- **THEN** the system MUST return the available entry names together with their mapped source, preset, and resolved command metadata

#### Scenario: Caller inspects a catalog entry execution plan
- **WHEN** a caller executes the catalog planning command for a named entry
- **THEN** the system MUST return the resolved dispatch metadata and merged arguments without executing the underlying workflow

### Requirement: Command catalog CLI SHALL support named multi-step bundles composed from existing catalog entries
The system SHALL allow callers to define a named bundle that references multiple existing catalog entries and executes them sequentially through the existing single-entry dispatch path.

#### Scenario: Caller lists available catalog bundles
- **WHEN** a caller executes the catalog listing command for bundles
- **THEN** the system MUST return the available bundle names together with their resolved step metadata

#### Scenario: Caller inspects a catalog bundle execution plan
- **WHEN** a caller executes the catalog planning command for a named bundle
- **THEN** the system MUST return the selected step range together with each step's resolved dispatch metadata and merged arguments without executing any underlying workflow
