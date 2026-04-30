## ADDED Requirements

### Requirement: Query API management SHALL expose market transaction queries through the transaction domain
The system SHALL expose market transaction data queries through the existing `transaction` domain on `TdxApiManager` instead of placing them inside `market`.

#### Scenario: Caller requests market transaction data through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke time-range market transaction queries through `manager.transaction.market_transaction_data(...)`

#### Scenario: Caller requests dated market transaction data through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke dated market transaction queries through `manager.transaction.market_transaction_data_by_date(...)`

### Requirement: Query API management SHALL keep market transaction queries profile-agnostic and field-explicit
The system SHALL keep market transaction query methods independent from profile file loading and SHALL require market transaction `field_list` values to be passed explicitly instead of resolving them from API profile defaults.

#### Scenario: Transaction domain delegates market parameters without reading profile files
- **WHEN** a manager-driven market transaction query is invoked
- **THEN** the `transaction` domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

#### Scenario: Market transaction fields are not inferred from API profile defaults
- **WHEN** a caller invokes a manager market transaction query
- **THEN** the manager MUST use the explicitly provided market transaction field list rather than resolving a default field list from the selected API profile

### Requirement: Query API management SHALL preserve official latest-record semantics for dated market transaction data
The system SHALL preserve the official runtime behavior that `year=0` and `mmdd=0` request the latest available market transaction record.

#### Scenario: Caller requests latest dated market transaction record
- **WHEN** a caller invokes `manager.transaction.market_transaction_data_by_date(...)` with `year=0` and `mmdd=0`
- **THEN** the manager MUST pass those zero values through unchanged to the bridge layer
