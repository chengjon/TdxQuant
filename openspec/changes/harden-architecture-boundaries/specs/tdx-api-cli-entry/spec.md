## ADDED Requirements

### Requirement: Query API CLI SHALL allow nested api parser ownership to live outside the root CLI module
The system SHALL allow the nested `api` command group parser and dispatcher to be owned by a dedicated API CLI module while preserving the public root `tdxquant.cli` entrypoint.

#### Scenario: Root CLI builds nested api command through API command module
- **WHEN** the root parser is constructed
- **THEN** the root CLI MUST register the nested `api` command group through the API command module
- **AND** existing nested `api` subcommand names and arguments MUST remain available

#### Scenario: Root CLI dispatches nested api command through API command module
- **WHEN** a caller invokes a nested `api` subcommand
- **THEN** root CLI handling MUST delegate execution to the API command module
- **AND** the command MUST still dispatch through the same manager-backed behavior as before extraction

#### Scenario: Flat command compatibility is not changed by api extraction
- **WHEN** the nested `api` command family is extracted
- **THEN** existing flat bridge and desktop commands MUST remain registered through the root CLI compatibility layer
