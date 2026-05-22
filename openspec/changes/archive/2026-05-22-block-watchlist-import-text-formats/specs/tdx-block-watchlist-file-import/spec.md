## ADDED Requirements

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

