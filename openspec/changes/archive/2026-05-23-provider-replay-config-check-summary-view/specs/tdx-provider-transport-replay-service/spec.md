## MODIFIED Requirements

### Requirement: Provider transport replay service SHALL expose foreground CLI startup

The system SHALL provide a CLI entry that loads a replay transport config and delegates to the existing foreground provider replay HTTP server.

#### Scenario: Caller validates a replay service config without opening a socket

- **WHEN** a caller executes `provider-replay config-check --config <path>`
- **THEN** the CLI MUST load the replay transport config and return a machine-readable summary
- **AND** the command MUST NOT start the HTTP server

#### Scenario: Caller requests a config-check summary view

- **WHEN** a caller executes `provider-replay config-check --config <path> --view summary`
- **THEN** the CLI MUST include a machine-readable `summary_view` derived from the loaded config
- **AND** the summary MUST indicate that the command did not start serving, did not request probes, and does not provide daemon lifecycle management
- **AND** the command MUST NOT expose bearer token values

#### Scenario: Caller starts the replay service in the foreground

- **WHEN** a caller executes `provider-replay serve --config <path>`
- **THEN** the CLI MUST load the replay transport config and call the existing foreground server runner
- **AND** the command MUST NOT imply daemon start/stop lifecycle management
