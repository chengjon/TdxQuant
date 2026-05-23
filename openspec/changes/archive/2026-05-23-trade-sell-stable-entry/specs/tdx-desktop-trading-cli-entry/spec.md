## ADDED Requirements

### Requirement: Trade CLI SHALL expose a stable sell subcommand

The stable nested trade CLI SHALL expose Ping An sell through the dedicated `trade` command group rather than relying only on generic order placement or manager internals.

#### Scenario: Caller uses nested trade sell command

- **WHEN** a caller executes `trade sell`
- **THEN** the CLI MUST dispatch a stable sell request through the trade service path
- **AND** the request MUST use sell side
- **AND** the command MUST accept the same stable safety controls as `trade buy`

#### Scenario: Caller uses trade sell with safety controls

- **WHEN** a caller executes `trade sell` with `submission_key` or `max_price`
- **THEN** those controls MUST be forwarded unchanged to the stable sell workflow
