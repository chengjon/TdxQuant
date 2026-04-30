## MODIFIED Requirements

### Requirement: Command catalog CLI SHALL expose a unified daily entry registry
The system SHALL provide a top-level command catalog that lists stable daily entries mapped to existing `task`, `report`, or `trade` preset workflows.

#### Scenario: Caller requests a summary view for a catalog list
- **WHEN** a caller executes a catalog listing command with summary output enabled
- **THEN** the system MUST return a reduced discovery-oriented summary view instead of the full detailed list payload

#### Scenario: Caller receives stable catalog list ordering
- **WHEN** a caller executes the catalog listing command repeatedly with the same filter set
- **THEN** the system MUST return entries and bundles in a stable deterministic order
