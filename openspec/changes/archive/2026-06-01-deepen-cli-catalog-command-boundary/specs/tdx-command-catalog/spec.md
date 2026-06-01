## ADDED Requirements

### Requirement: Command catalog CLI SHALL preserve behavior through a dedicated catalog command boundary
The command catalog CLI SHALL register and handle catalog subcommands through a catalog-specific command boundary while preserving the existing public catalog command surface and payload contracts.

#### Scenario: Caller lists catalog entries through the catalog command boundary
- **WHEN** a caller invokes `catalog list` with existing filters and summary-view options
- **THEN** the command MUST return the same discovery-oriented entry or bundle payload shape as before the boundary extraction
- **AND** the command MUST NOT dispatch task, report, trade, or bundle execution

#### Scenario: Caller plans or previews catalog targets through the catalog command boundary
- **WHEN** a caller invokes `catalog plan` or `catalog preview` for an entry or bundle target
- **THEN** the command MUST return the existing non-executing resolved target metadata, provenance, constraints, and summary fields
- **AND** the command MUST NOT dispatch task, report, trade, or bundle execution

#### Scenario: Caller validates the catalog registry through the catalog command boundary
- **WHEN** a caller invokes `catalog validate`
- **THEN** the command MUST validate catalog entries and bundles using the existing registry checks
- **AND** the command MUST NOT dispatch task, report, trade, or bundle execution

#### Scenario: Caller runs a catalog target through the catalog command boundary
- **WHEN** a caller invokes `catalog run`
- **THEN** the command MUST continue to use the existing resolved catalog execution path
- **AND** the change MUST NOT introduce new workflow-builder semantics beyond existing catalog run dispatch behavior
