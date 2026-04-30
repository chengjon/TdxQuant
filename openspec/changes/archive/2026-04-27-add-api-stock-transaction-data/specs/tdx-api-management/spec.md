## ADDED Requirements

### Requirement: Query API management SHALL expose stock transaction queries through a dedicated transaction domain
The system SHALL expose stock transaction data queries through a dedicated `transaction` domain on `TdxApiManager` instead of placing them inside `market`.

#### Scenario: Caller requests stock transaction data through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke time-range stock transaction queries through `manager.transaction.stock_transaction_data(...)`

#### Scenario: Caller requests dated stock transaction data through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke dated stock transaction queries through `manager.transaction.stock_transaction_data_by_date(...)`

### Requirement: Query API management SHALL keep stock transaction queries profile-agnostic and field-explicit
The system SHALL keep the `transaction` domain independent from profile file loading and SHALL require stock transaction `field_list` values to be passed explicitly instead of resolving them from API profile defaults.

#### Scenario: Transaction domain delegates explicit parameters without reading profile files
- **WHEN** a manager-driven stock transaction query is invoked
- **THEN** the `transaction` domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

#### Scenario: Stock transaction fields are not inferred from API profile defaults
- **WHEN** a caller invokes a manager stock transaction query
- **THEN** the manager MUST use the explicitly provided stock transaction field list rather than resolving a default field list from the selected API profile

### Requirement: Query API management SHALL preserve official latest-record semantics for dated stock transaction data
The system SHALL preserve the official runtime behavior that `year=0` and `mmdd=0` request the latest available stock transaction record.

#### Scenario: Caller requests latest dated stock transaction record
- **WHEN** a caller invokes `manager.transaction.stock_transaction_data_by_date(...)` with `year=0` and `mmdd=0`
- **THEN** the manager MUST pass those zero values through unchanged to the bridge layer
