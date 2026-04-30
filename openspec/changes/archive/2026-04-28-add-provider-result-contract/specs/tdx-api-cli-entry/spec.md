## MODIFIED Requirements

### Requirement: Query API CLI SHALL support profile-driven daily usage
The system SHALL allow the nested `api` command group to accept a profile selection and standard output path controls for daily usage while emitting structured machine-readable output through the provider-facing synchronous result envelope.

#### Scenario: Caller selects an api profile
- **WHEN** a caller invokes a nested `api` query command with `--profile`
- **THEN** the command MUST resolve the named API profile and apply it through the manager layer

#### Scenario: Caller requests structured output from api command
- **WHEN** a caller invokes a nested `api` query command with an output destination
- **THEN** the command MUST write the structured result using the provider-facing synchronous result envelope

## ADDED Requirements

### Requirement: Query API CLI SHALL align JSON-oriented outputs with the provider result contract
The system SHALL use the same provider-facing synchronous result envelope for nested `api` outputs and flat bridge JSON-oriented outputs so that upstream systems can consume one stable machine contract.

#### Scenario: Nested api command writes provider-facing JSON envelope
- **WHEN** a caller requests structured JSON-oriented output from a nested `api` command
- **THEN** the CLI MUST serialize the result using the provider-facing synchronous result envelope

#### Scenario: Flat bridge command writes provider-facing JSON envelope
- **WHEN** a caller requests structured JSON-oriented output from a flat bridge query command
- **THEN** the CLI MUST serialize the result using the same provider-facing synchronous result envelope used by nested `api` commands

### Requirement: Query API CLI SHALL preserve JSON failure structure alongside exit-code semantics
The system SHALL preserve machine-readable JSON failure output for JSON-oriented CLI calls while also using stable process exit code semantics.

#### Scenario: Successful JSON-oriented CLI call exits cleanly
- **WHEN** a JSON-oriented nested `api` or flat bridge query command succeeds
- **THEN** the CLI process MUST exit with code `0`

#### Scenario: Failed JSON-oriented CLI call preserves structured failure output
- **WHEN** a JSON-oriented nested `api` or flat bridge query command fails
- **THEN** the CLI process MUST exit with a non-zero code
- **AND** the CLI MUST still emit the provider-facing synchronous result envelope describing the failure
