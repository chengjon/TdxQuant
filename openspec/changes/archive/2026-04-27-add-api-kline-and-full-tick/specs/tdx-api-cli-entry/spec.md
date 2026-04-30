## MODIFIED Requirements

### Requirement: Query API CLI SHALL provide a nested api command group
The system SHALL provide a nested `api` command group for query-oriented TdxQuant access in addition to the existing flat CLI commands.

#### Scenario: Caller invokes nested api formula command
- **WHEN** a caller invokes a supported formula-related `api` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager` rather than directly through a flat command handler

#### Scenario: Caller invokes nested api block command
- **WHEN** a caller invokes a supported block-related `api` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager` rather than directly through a flat command handler

#### Scenario: Caller invokes nested api kline command
- **WHEN** a caller invokes the nested `api kline` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.market.kline(...)`

#### Scenario: Caller invokes nested api full-tick command
- **WHEN** a caller invokes the nested `api full-tick` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.market.full_tick(...)`

### Requirement: Query API CLI SHALL preserve existing flat command compatibility
The system SHALL keep existing flat query commands functional while introducing the new nested `api` command group.

#### Scenario: Existing formula command remains available during migration
- **WHEN** a caller invokes an existing flat formula-related command during the expansion phase
- **THEN** that command MUST remain usable while the nested `api` group is being expanded

#### Scenario: Existing user-block command remains available during migration
- **WHEN** a caller invokes `tdx-send-user-block` during the expansion phase
- **THEN** that command MUST remain usable while the nested `api` group is being expanded

#### Scenario: Existing flat kline command remains available during migration
- **WHEN** a caller invokes `tdx-data-kline` during the expansion phase
- **THEN** that command MUST remain usable while the nested `api` group is being expanded
