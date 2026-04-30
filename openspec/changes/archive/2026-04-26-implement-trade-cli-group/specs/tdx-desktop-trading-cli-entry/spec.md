## MODIFIED Requirements

### Requirement: Desktop trading CLI SHALL evolve toward a dedicated nested trade command group
The system SHALL define desktop automation trading CLI standardization around a dedicated nested `trade` command group rather than extending the query-oriented `api` command group.

#### Scenario: Future nested trading CLI is introduced
- **WHEN** the project introduces a standardized nested CLI entry for desktop trading
- **THEN** that entry MUST be represented as a `trade` command group or an equivalently dedicated trading namespace

#### Scenario: Trading commands are not merged into api namespace
- **WHEN** a desktop trading command is standardized at the CLI layer
- **THEN** it MUST NOT require callers to use the query-oriented `api` namespace

#### Scenario: Caller uses nested trade buy command
- **WHEN** a caller executes the stable Ping An desktop buy workflow from the standardized CLI layer
- **THEN** the system MUST expose that workflow through a nested `trade buy` style command

#### Scenario: Caller uses nested trade submit-once command
- **WHEN** a caller executes the stable Ping An submit-once desktop workflow from the standardized CLI layer
- **THEN** the system MUST expose that workflow through a nested `trade submit-once` style command
