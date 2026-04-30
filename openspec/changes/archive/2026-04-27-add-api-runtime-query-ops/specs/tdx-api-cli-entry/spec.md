## MODIFIED Requirements

### Requirement: Query API CLI SHALL provide a nested api command group
The system SHALL provide a nested `api` command group for query-oriented TdxQuant access in addition to the existing flat CLI commands.

#### Scenario: Caller invokes nested api trading-dates command
- **WHEN** a caller invokes the nested `api trading-dates` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.runtime.trading_dates(...)`

#### Scenario: Caller invokes nested api refresh-kline command
- **WHEN** a caller invokes the nested `api refresh-kline` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.runtime.refresh_kline(...)`

#### Scenario: Caller invokes nested api download-file command
- **WHEN** a caller invokes the nested `api download-file` subcommand
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.runtime.download_file(...)`

## ADDED Requirements

### Requirement: Query API CLI SHALL expose flat bridge commands for runtime public query actions
The system SHALL expose flat bridge commands for runtime public query actions so that bridge-oriented callers can use the same capabilities without going through the manager layer.

#### Scenario: Caller invokes flat trading-dates bridge command
- **WHEN** a caller invokes `tdx-get-trading-dates`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_trading_dates`

#### Scenario: Caller invokes flat refresh-kline bridge command
- **WHEN** a caller invokes `tdx-refresh-kline`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `refresh_kline`

#### Scenario: Caller invokes flat download-file bridge command
- **WHEN** a caller invokes `tdx-download-file`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `download_file`
