# tdx-block-watchlist-file-import Delta

## ADDED Requirements

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
