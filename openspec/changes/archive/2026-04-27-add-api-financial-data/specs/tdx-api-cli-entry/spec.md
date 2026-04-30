## ADDED Requirements

### Requirement: Query API CLI SHALL provide nested api commands for professional financial queries
The system SHALL expose professional financial data through nested `api` subcommands that dispatch through `TdxApiManager.financial`.

#### Scenario: Caller invokes nested api financial-data command
- **WHEN** a caller invokes `api financial-data`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.financial.financial_data(...)`

#### Scenario: Caller invokes nested api financial-data-by-date command
- **WHEN** a caller invokes `api financial-data-by-date`
- **THEN** the CLI MUST dispatch the call through `TdxApiManager.financial.financial_data_by_date(...)`

### Requirement: Query API CLI SHALL expose flat bridge commands for professional financial queries
The system SHALL keep flat bridge-oriented CLI access available for professional financial queries alongside the nested `api` manager path.

#### Scenario: Caller invokes flat financial-data bridge command
- **WHEN** a caller invokes `tdx-data-financial`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_financial_data`

#### Scenario: Caller invokes flat financial-data-by-date bridge command
- **WHEN** a caller invokes `tdx-data-financial-by-date`
- **THEN** the CLI MUST dispatch the call to the dedicated bridge wrapper for `get_financial_data_by_date`

### Requirement: Query API CLI SHALL require explicit professional financial field selection
The system SHALL require callers to pass professional financial fields explicitly on CLI entrypoints instead of silently filling them from an API profile.

#### Scenario: Nested api financial-data command receives explicit fields
- **WHEN** a caller invokes `api financial-data` or `api financial-data-by-date`
- **THEN** the CLI MUST collect an explicit professional financial field list from the command arguments and pass it through unchanged

#### Scenario: Professional financial CLI command omits fields
- **WHEN** a caller invokes a professional financial CLI command without any field arguments
- **THEN** the CLI MUST reject the request before dispatching it to the manager or bridge layer
