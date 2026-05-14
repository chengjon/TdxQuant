# tdx-block-watchlist-file-import Specification

## Purpose
TBD - created by archiving change block-watchlist-file-import. Update Purpose after archive.
## Requirements
### Requirement: Block watchlist file import SHALL define an explicit JSON input schema
The system SHALL support a JSON object input schema for importing file-backed watchlists into block sync.

#### Scenario: Import file contains a valid minimal watchlist
- **WHEN** a caller loads a watchlist import file with `schema_version`, `block_code`, and `symbols`
- **THEN** the parser MUST return normalized block code and symbol list data
- **AND** the default sync mode MUST be `replace`

#### Scenario: Import file may preserve non-sync source metadata
- **WHEN** a caller loads symbol objects that include a `symbol` field and additional metadata
- **THEN** the parser MUST use the `symbol` field for sync
- **AND** it MUST NOT require extra metadata fields to be part of the sync request

### Requirement: Block watchlist file import SHALL validate malformed input before sync
The system SHALL reject malformed import files before invoking block sync.

#### Scenario: Import file rejects missing symbols
- **WHEN** a caller loads an import file without a non-empty `symbols` array
- **THEN** the parser MUST return or raise a stable validation failure
- **AND** block sync MUST NOT be invoked

#### Scenario: Import file rejects invalid symbol entries
- **WHEN** a caller loads an import file containing an empty symbol or malformed symbol object
- **THEN** the parser MUST identify the invalid entry
- **AND** block sync MUST NOT be invoked

### Requirement: Block watchlist file import SHALL expose dry-run planning output
The system SHALL expose a dry-run plan for imported watchlists before callers execute block sync.

#### Scenario: Dry-run plan returns normalized request
- **WHEN** a caller plans an imported watchlist file
- **THEN** the plan MUST include block code, mode, create-if-missing flag, normalized symbols, symbol count, and source path
- **AND** the plan MUST identify whether execution would be a dry run

### Requirement: Block watchlist file import SHALL delegate execution to block sync
The system SHALL connect validated imported watchlists to the existing `block.sync_watchlist` implementation.

#### Scenario: Imported watchlist executes through block sync
- **WHEN** a caller executes an imported watchlist file
- **THEN** the adapter MUST call the existing block sync function with normalized symbols and import options
- **AND** it MUST preserve `mode`, `create_if_missing`, `dry_run`, and `mutation_key`

