## ADDED Requirements

### Requirement: Command catalog SHALL be compatible with central runtime config loading
The system SHALL allow command catalog and command bundle loading to use the central runtime configuration registry without changing existing catalog entry or bundle semantics.

#### Scenario: Catalog loader uses registered runtime path
- **WHEN** command catalog loading is migrated to the central runtime config registry
- **THEN** it MUST continue to resolve `runtime/command-catalog.json` from the project root
- **AND** it MUST return the same parsed catalog object semantics as before migration

#### Scenario: Command bundle loader uses registered runtime path
- **WHEN** command bundle loading is migrated to the central runtime config registry
- **THEN** it MUST continue to resolve `runtime/command-bundles.json` from the project root
- **AND** it MUST return the same parsed bundle object semantics as before migration

### Requirement: Command catalog SHALL allow capability risk metadata to be surfaced without changing execution
The system SHALL allow catalog entries and validation summaries to include capability risk metadata while preserving existing catalog execution dispatch.

#### Scenario: Catalog entry exposes risk metadata
- **WHEN** a catalog entry is associated with a known capability risk classification
- **THEN** catalog-facing metadata MAY expose the classification as read-only metadata
- **AND** the classification MUST NOT change dispatch or execution behavior by itself
