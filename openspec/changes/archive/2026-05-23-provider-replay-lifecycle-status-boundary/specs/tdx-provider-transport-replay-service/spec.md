## ADDED Requirements

### Requirement: Provider transport replay service SHALL expose lifecycle boundary status

The system SHALL provide a replay fake-provider status summary that distinguishes configured replay capabilities from managed daemon lifecycle support.

#### Scenario: Caller inspects replay fake-provider status without starting a server

- **WHEN** a caller builds replay fake-provider status from a valid provider transport replay config
- **THEN** the status MUST identify the provider, bind address, configured replay source, and replay-only transport mode
- **AND** it MUST list the read-only HTTP endpoints covered by the fake-provider surface
- **AND** it MUST state that runtime state is not observed by this summary
- **AND** it MUST state that daemon start/stop lifecycle management is not provided

#### Scenario: Caller requests replay fake-provider status through the CLI

- **WHEN** a caller executes `provider-replay status --config <path>`
- **THEN** the CLI MUST load the replay transport config and return the lifecycle boundary status
- **AND** the command MUST NOT open a socket or start the foreground server
- **AND** the command MUST NOT imply live market session support
