## ADDED Requirements

### Requirement: Trade CLI SHALL expose broker-neutral securities order commands
The system SHALL expose broker-neutral nested trade CLI commands for canonical securities order placement and canonical tracked-order query.

#### Scenario: Caller uses trade order-place for a buy order
- **WHEN** a caller executes `trade order-place` with a first-phase A-share limit order and `side=buy`
- **THEN** the CLI MUST dispatch the request through the canonical securities trader gateway path
- **AND** the resolved command contract MUST accept broker selection and the canonical order fields required by the first phase

#### Scenario: Caller uses trade order-place for a sell order
- **WHEN** a caller executes `trade order-place` with a first-phase A-share limit order and `side=sell`
- **THEN** the CLI MUST route the order through the same canonical command family used for buy orders
- **AND** the CLI MUST preserve the explicit order side in the resolved request

#### Scenario: Caller queries tracked orders and trades through broker-neutral commands
- **WHEN** a caller executes `trade order-query` or `trade trade-query`
- **THEN** the CLI MUST dispatch the request through the canonical trader query path
- **AND** the returned result MUST describe canonical tracked orders or canonical tracked trades rather than PingAn-only command payloads

### Requirement: Trade CLI SHALL preserve compatibility commands during trader-gateway migration
The system SHALL keep the existing nested PingAn trade commands available while the canonical trader gateway is introduced.

#### Scenario: Existing trade buy command remains usable
- **WHEN** a caller executes the existing `trade buy` command during the migration period
- **THEN** the command MUST remain available
- **AND** the implementation MAY satisfy that command by forwarding it into the canonical order-placement path with `side=buy`

#### Scenario: Existing trade submit-once command remains usable
- **WHEN** a caller executes `trade submit-once` during the migration period
- **THEN** the command MUST remain available
- **AND** the implementation MAY map it to the canonical gateway through a PingAn immediate-confirm execution mode while preserving the existing caller contract

#### Scenario: Existing PingAn boundary commands remain explicit
- **WHEN** a caller executes `trade submit-ready` or `trade confirm-current`
- **THEN** the CLI MUST continue to expose those commands as PingAn desktop boundary workflows
- **AND** those commands MUST NOT redefine the canonical broker-neutral order placement contract
