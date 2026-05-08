## MODIFIED Requirements

### Requirement: Query API CLI SHALL support profile-driven daily usage
The system SHALL allow the nested `api` command group to accept a profile selection and standard output path controls for daily usage while emitting structured machine-readable output through the provider-facing synchronous result envelope.

#### Scenario: Caller selects an api profile
- **WHEN** a caller invokes a nested `api` query command with `--profile`
- **THEN** the command MUST resolve the named API profile and apply it through the manager layer

#### Scenario: Caller requests structured output from api command
- **WHEN** a caller invokes a nested `api` query command with an output destination
- **THEN** the command MUST write the structured result using the hardened provider-facing synchronous result envelope

#### Scenario: CLI provider failure preserves JSON structure and shell failure semantics
- **WHEN** a nested `api` command returns a failed synchronous provider result
- **THEN** the command MUST still emit the hardened provider-facing synchronous result envelope
- **AND** the command MUST exit with a non-zero process status for the failed provider call
