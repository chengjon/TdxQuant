## ADDED Requirements

### Requirement: Command catalog SHALL validate fixed registry entries without execution

The command catalog CLI SHALL provide a non-execution validation path that checks
selected catalog entries and bundles resolve through the existing registry
metadata and reports task/report bundle coverage.

#### Scenario: Caller validates the full catalog registry

- **WHEN** a caller runs `catalog validate --kind all`
- **THEN** the system MUST resolve all selected catalog entries and bundles without executing any task, report, trade, or bundle step
- **AND** the result MUST include entry count, bundle count, task/report bundle count, invalid count, and validation status

#### Scenario: Caller validates follow-up bundles by label

- **WHEN** a caller runs `catalog validate --kind bundle --label followup`
- **THEN** the system MUST validate only selected bundles with that label
- **AND** the task/report bundle count MUST reflect bundles whose resolved steps include both task and report sources

#### Scenario: Caller validates an unsupported target

- **WHEN** a caller runs `catalog validate` for a missing entry or bundle
- **THEN** the system MUST return an invalid-request result with a structured error
- **AND** it MUST NOT execute any selected catalog target
