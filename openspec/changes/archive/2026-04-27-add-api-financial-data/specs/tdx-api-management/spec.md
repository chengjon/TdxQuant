## ADDED Requirements

### Requirement: Query API management SHALL expose professional financial queries through a dedicated financial domain
The system SHALL expose professional financial data queries through a dedicated `financial` domain on `TdxApiManager` instead of placing them inside `market` or `meta`.

#### Scenario: Caller requests professional financial data through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke time-range professional financial queries through `manager.financial.financial_data(...)`

#### Scenario: Caller requests dated professional financial data through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke dated professional financial queries through `manager.financial.financial_data_by_date(...)`

### Requirement: Query API management SHALL keep professional financial queries profile-agnostic and field-explicit
The system SHALL keep the `financial` domain independent from profile file loading and SHALL require the manager call site to pass professional financial `field_list` explicitly instead of filling those fields from API profile defaults.

#### Scenario: Financial domain delegates explicit parameters without reading profile files
- **WHEN** a manager-driven professional financial query is invoked
- **THEN** the `financial` domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

#### Scenario: Professional financial fields are not inferred from API profile defaults
- **WHEN** a caller invokes a manager financial query
- **THEN** the manager MUST use the explicitly provided professional financial field list rather than resolving a default field list from the selected API profile
