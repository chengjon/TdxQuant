## ADDED Requirements

### Requirement: Trade CLI SHALL expose a stable broker-capabilities subcommand
The system SHALL expose a stable nested `trade broker-capabilities` CLI entrypoint for the non-executing PingAn desktop extended broker capability probe.

#### Scenario: Caller uses nested trade broker-capabilities command
- **WHEN** a caller executes `trade broker-capabilities`
- **THEN** the CLI MUST dispatch the extended broker capability probe
- **AND** the command MUST NOT execute funds query, positions query, cancel order, or broker-native push subscription

#### Scenario: Caller selects PingAn desktop broker capability boundary
- **WHEN** a caller executes `trade broker-capabilities --broker pingan_desktop`
- **THEN** the CLI MUST return PingAn desktop capability metadata
- **AND** the command MUST reject unsupported broker names rather than falling back to another broker
