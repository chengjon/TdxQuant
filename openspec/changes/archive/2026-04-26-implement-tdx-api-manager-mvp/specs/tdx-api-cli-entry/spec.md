## ADDED Requirements

### Requirement: Query API CLI SHALL provide a nested api command group
The system SHALL provide a nested `api` command group for query-oriented TdxQuant access in addition to the existing flat CLI commands.

#### Scenario: Caller requests api command help
- **WHEN** a caller invokes the CLI help for the `api` command group
- **THEN** the CLI MUST list the supported query-oriented subcommands exposed by the MVP scope

#### Scenario: Caller invokes a nested api query command
- **WHEN** a caller invokes a supported `api` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager` rather than directly through a flat command handler

### Requirement: Query API CLI SHALL preserve existing flat command compatibility
The system SHALL keep existing flat query commands functional while introducing the new nested `api` command group.

#### Scenario: Existing flat query command remains available
- **WHEN** a caller invokes an existing flat query command that was already supported before the MVP change
- **THEN** the command MUST remain usable after the new `api` command group is added

#### Scenario: Existing non-MVP capabilities remain on old entrypoints
- **WHEN** a caller invokes `send_user_block` or formula-related capabilities during the MVP phase
- **THEN** those capabilities MUST continue to use their existing entrypoints and MUST NOT be required to move to the new `api` command group

### Requirement: Query API CLI SHALL support profile-driven daily usage
The system SHALL allow the nested `api` command group to accept a profile selection and standard output path controls for daily usage.

#### Scenario: Caller selects an api profile
- **WHEN** a caller invokes a nested `api` query command with `--profile`
- **THEN** the command MUST resolve the named API profile and apply it through the manager layer

#### Scenario: Caller requests structured output from api command
- **WHEN** a caller invokes a nested `api` query command with an output destination
- **THEN** the command MUST write the structured result using the same JSON-oriented result contract used by the current CLI
