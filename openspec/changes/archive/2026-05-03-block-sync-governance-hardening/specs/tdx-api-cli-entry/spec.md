## MODIFIED Requirements

### Requirement: Query API CLI SHALL provide a nested api command group
The system SHALL provide a nested `api` command group for query-oriented TdxQuant access in addition to the existing flat CLI commands.

#### Scenario: Caller invokes nested api divid-factors command
- **WHEN** a caller invokes the nested `api divid-factors` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.meta.divid_factors(...)`

#### Scenario: Caller invokes nested api ipo-info command
- **WHEN** a caller invokes the nested `api ipo-info` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.meta.ipo_info(...)`

#### Scenario: Caller invokes nested api block-sync command
- **WHEN** a caller invokes `api block-sync`
- **THEN** the CLI MUST dispatch the call through the manager-backed block sync capability

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

#### Scenario: Existing flat send-user-block command remains available during migration
- **WHEN** a caller invokes `tdx-send-user-block` during the expansion phase after block lifecycle expansion
- **THEN** that command MUST remain usable alongside the new custom-sector lifecycle commands

#### Scenario: Caller invokes flat block-sync command during migration
- **WHEN** a caller invokes `tdx-block-sync`
- **THEN** the CLI MUST dispatch the call to the dedicated block sync wrapper while preserving existing block write commands
