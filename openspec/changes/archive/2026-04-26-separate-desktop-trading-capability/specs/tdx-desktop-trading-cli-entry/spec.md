## ADDED Requirements

### Requirement: Desktop trading CLI SHALL evolve toward a dedicated nested trade command group
The system SHALL define desktop automation trading CLI standardization around a dedicated nested `trade` command group rather than extending the query-oriented `api` command group.

#### Scenario: Future nested trading CLI is introduced
- **WHEN** the project introduces a standardized nested CLI entry for desktop trading
- **THEN** that entry MUST be represented as a `trade` command group or an equivalently dedicated trading namespace

#### Scenario: Trading commands are not merged into api namespace
- **WHEN** a desktop trading command is standardized at the CLI layer
- **THEN** it MUST NOT require callers to use the query-oriented `api` namespace

### Requirement: Desktop trading CLI SHALL preserve flat-command compatibility during migration
The system SHALL preserve existing flat desktop trading commands while the future nested trade CLI is being planned and introduced.

#### Scenario: Existing flat trade command remains compatible
- **WHEN** the project defines the future `trade` CLI direction
- **THEN** existing flat commands such as `pingan-buy-submit-once`, `pingan-buy`, and related diagnostic commands MUST continue to operate during the migration period

#### Scenario: Stable and experimental commands can be separated later
- **WHEN** a future nested `trade` CLI is designed in detail
- **THEN** the system MAY separate stable trading commands from diagnostic or experimental commands without breaking the existing flat compatibility contract
