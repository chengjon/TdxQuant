## ADDED Requirements

### Requirement: Query API CLI SHALL provide nested api commands for market transaction queries
The system SHALL expose market transaction data through nested `api` subcommands that dispatch through `TdxApiManager.transaction`.

#### Scenario: Caller invokes nested api market-transaction-data command
- **WHEN** a caller invokes `api market-transaction-data`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.transaction.market_transaction_data(...)`

#### Scenario: Caller invokes nested api market-transaction-data-by-date command
- **WHEN** a caller invokes `api market-transaction-data-by-date`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.transaction.market_transaction_data_by_date(...)`

### Requirement: Query API CLI SHALL expose flat bridge commands for market transaction queries
The system SHALL keep flat bridge-oriented CLI access available for market transaction queries alongside the nested `api` manager path.

#### Scenario: Caller invokes flat market-transaction bridge command
- **WHEN** a caller invokes `tdx-data-market-transaction`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_scjy_value`

#### Scenario: Caller invokes flat market-transaction-by-date bridge command
- **WHEN** a caller invokes `tdx-data-market-transaction-by-date`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_scjy_value_by_date`

### Requirement: Query API CLI SHALL require explicit market transaction field selection and preserve zero-date semantics
The system SHALL require callers to pass market transaction fields explicitly, SHALL not require any stock code list, and SHALL preserve the official `year=0, mmdd=0` latest-record semantics for dated calls.

#### Scenario: CLI market transaction command omits fields
- **WHEN** a caller invokes a market transaction CLI command without any field arguments
- **THEN** the CLI MUST reject the request before dispatching it to the manager or bridge layer

#### Scenario: CLI market transaction command does not require stock codes
- **WHEN** a caller invokes a market transaction CLI command with explicit field arguments and no stock code arguments
- **THEN** the CLI MUST accept the command and dispatch it without constructing a stock list

#### Scenario: CLI dated market transaction command uses zero-date latest-record query
- **WHEN** a caller invokes a dated market transaction CLI command with `--year 0 --mmdd 0`
- **THEN** the CLI MUST pass those zero values through unchanged
