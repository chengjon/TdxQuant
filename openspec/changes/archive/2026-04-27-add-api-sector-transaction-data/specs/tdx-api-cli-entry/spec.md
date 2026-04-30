## ADDED Requirements

### Requirement: Query API CLI SHALL provide nested api commands for sector transaction queries
The system SHALL expose sector transaction data through nested `api` subcommands that dispatch through `TdxApiManager.transaction`.

#### Scenario: Caller invokes nested api sector-transaction-data command
- **WHEN** a caller invokes `api sector-transaction-data`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.transaction.sector_transaction_data(...)`

#### Scenario: Caller invokes nested api sector-transaction-data-by-date command
- **WHEN** a caller invokes `api sector-transaction-data-by-date`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.transaction.sector_transaction_data_by_date(...)`

### Requirement: Query API CLI SHALL expose flat bridge commands for sector transaction queries
The system SHALL keep flat bridge-oriented CLI access available for sector transaction queries alongside the nested `api` manager path.

#### Scenario: Caller invokes flat sector-transaction bridge command
- **WHEN** a caller invokes `tdx-data-sector-transaction`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_bkjy_value`

#### Scenario: Caller invokes flat sector-transaction-by-date bridge command
- **WHEN** a caller invokes `tdx-data-sector-transaction-by-date`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_bkjy_value_by_date`

### Requirement: Query API CLI SHALL require explicit sector transaction field selection and preserve zero-date semantics
The system SHALL require callers to pass sector transaction fields explicitly and SHALL preserve the official `year=0, mmdd=0` latest-record semantics for dated calls.

#### Scenario: CLI sector transaction command omits fields
- **WHEN** a caller invokes a sector transaction CLI command without any field arguments
- **THEN** the CLI MUST reject the request before dispatching it to the manager or bridge layer

#### Scenario: CLI dated sector transaction command uses zero-date latest-record query
- **WHEN** a caller invokes a dated sector transaction CLI command with `--year 0 --mmdd 0`
- **THEN** the CLI MUST pass those zero values through unchanged
