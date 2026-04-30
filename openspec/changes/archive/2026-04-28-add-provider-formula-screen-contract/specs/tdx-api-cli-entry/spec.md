## ADDED Requirements

### Requirement: Query API CLI SHALL provide a stable formula screen command
The system SHALL expose the stable formula screen contract through both nested `api` and flat bridge-oriented CLI entrypoints.

#### Scenario: Caller invokes nested api formula-screen command
- **WHEN** a caller invokes `api formula-screen`
- **THEN** the CLI MUST dispatch the call through the stable formula screen manager action rather than through the raw batch formula method

#### Scenario: Caller invokes flat formula-screen bridge command
- **WHEN** a caller invokes `tdx-formula-screen`
- **THEN** the CLI MUST dispatch the call to the dedicated stable formula screen bridge wrapper
