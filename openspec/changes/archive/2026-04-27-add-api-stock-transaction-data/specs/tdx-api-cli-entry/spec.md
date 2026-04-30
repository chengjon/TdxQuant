## ADDED Requirements

### Requirement: Query API CLI SHALL provide nested api commands for stock transaction queries
The system SHALL expose stock transaction data through nested `api` subcommands that dispatch through `TdxApiManager.transaction`.

#### Scenario: Caller invokes nested api stock-transaction-data command
- **WHEN** a caller invokes `api stock-transaction-data`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.transaction.stock_transaction_data(...)`

#### Scenario: Caller invokes nested api stock-transaction-data-by-date command
- **WHEN** a caller invokes `api stock-transaction-data-by-date`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.transaction.stock_transaction_data_by_date(...)`

### Requirement: Query API CLI SHALL expose flat bridge commands for stock transaction queries
The system SHALL keep flat bridge-oriented CLI access available for stock transaction queries alongside the nested `api` manager path.

#### Scenario: Caller invokes flat stock-transaction bridge command
- **WHEN** a caller invokes `tdx-data-stock-transaction`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_gpjy_value`

#### Scenario: Caller invokes flat stock-transaction-by-date bridge command
- **WHEN** a caller invokes `tdx-data-stock-transaction-by-date`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_gpjy_value_by_date`

### Requirement: Query API CLI SHALL require explicit stock transaction field selection and preserve zero-date semantics
The system SHALL require callers to pass stock transaction fields explicitly and SHALL preserve the official `year=0, mmdd=0` latest-record semantics for dated calls.

#### Scenario: CLI stock transaction command omits fields
- **WHEN** a caller invokes a stock transaction CLI command without any field arguments
- **THEN** the CLI MUST reject the request before dispatching it to the manager or bridge layer

#### Scenario: CLI dated stock transaction command uses zero-date latest-record query
- **WHEN** a caller invokes a dated stock transaction CLI command with `--year 0 --mmdd 0`
- **THEN** the CLI MUST pass those zero values through unchanged
