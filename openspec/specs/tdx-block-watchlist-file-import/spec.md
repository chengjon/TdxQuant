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

### Requirement: Block watchlist file import SHALL expose a task-level entry point

The system SHALL expose the existing JSON watchlist import adapter through a task command that accepts an import file path and delegates execution to the existing block sync governance path.

#### Scenario: Caller parses a task import command

- **WHEN** a caller invokes `task block-watchlist-import --input <path>`
- **THEN** the CLI MUST parse the input path and import execution controls

#### Scenario: Caller dispatches a task import command

- **WHEN** a caller dispatches `task block-watchlist-import`
- **THEN** the task manager MUST call the existing watchlist import adapter with the supplied input path
- **AND** it MUST preserve dry-run, show, and audit directory controls

#### Scenario: Invalid import input returns an invalid request result

- **WHEN** the task wrapper receives an unreadable or malformed import file
- **THEN** it MUST return an invalid request result before invoking block sync

### Requirement: Block watchlist file import SHALL parse CSV and TXT inputs

The watchlist import adapter SHALL accept CSV and TXT files and normalize them into the existing watchlist import request contract.

#### Scenario: CSV import normalizes rows

- **WHEN** a caller loads a CSV import file with `block_code` and `symbol` columns
- **THEN** the adapter MUST return a normalized import request with the shared block code and non-empty symbols
- **AND** optional metadata columns MUST map to the same request fields used by JSON imports

#### Scenario: TXT import normalizes directive metadata

- **WHEN** a caller loads a TXT import file with directive comments and symbol lines
- **THEN** the adapter MUST use the `block_code` directive as the target block
- **AND** non-empty non-comment lines MUST become normalized symbols

### Requirement: Block watchlist text imports SHALL reject malformed input before sync

The watchlist import adapter SHALL validate text imports before delegating to block sync.

#### Scenario: CSV import rejects missing required columns

- **WHEN** a caller loads a CSV import without `block_code` or `symbol`
- **THEN** the adapter MUST reject the file before invoking block sync

#### Scenario: CSV import rejects conflicting block codes

- **WHEN** a caller loads a CSV import whose rows contain multiple block codes
- **THEN** the adapter MUST reject the file before invoking block sync

#### Scenario: TXT import rejects missing target block

- **WHEN** a caller loads a TXT import without a `block_code` directive
- **THEN** the adapter MUST reject the file before invoking block sync

### Requirement: Block watchlist task import SHALL reuse text-format parsing

The task-level watchlist import entry point SHALL accept supported text formats through the existing `--input` path without adding a separate command.

#### Scenario: Task dry-run plans a text import

- **WHEN** a caller runs the task import path with a CSV or TXT input and dry-run enabled
- **THEN** the task manager MUST return the normalized import plan
- **AND** the task MUST NOT invoke provider mutation during dry-run

