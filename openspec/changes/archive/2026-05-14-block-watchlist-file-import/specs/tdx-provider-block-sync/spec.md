## ADDED Requirements

### Requirement: Provider block sync SHALL accept validated imported watchlists through an adapter
The system SHALL allow file-import adapters to feed validated watchlist symbols into the existing block sync path without changing the block sync mutation contract.

#### Scenario: Imported dry-run reuses block sync dry-run semantics
- **WHEN** a file-import adapter invokes block sync with `dry_run=true`
- **THEN** block sync MUST return its existing dry-run outcome shape
- **AND** it MUST NOT perform live block mutation writes

#### Scenario: Imported execution preserves sync governance options
- **WHEN** a file-import adapter invokes block sync with mode, create-if-missing, and mutation-key options
- **THEN** block sync MUST evaluate those options using the same governance rules as direct in-memory symbol-list sync
