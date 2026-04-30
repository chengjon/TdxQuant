## MODIFIED Requirements

### Requirement: Query API management SHALL provide a unified manager entrypoint
The system SHALL provide a `TdxApiManager` entrypoint for query-oriented TdxQuant capabilities so that callers do not need to invoke bridge functions directly for daily API workflows.

#### Scenario: Code caller uses manager to access runtime public query domain
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke runtime public query capabilities through `manager.runtime.<method>()`

### Requirement: Query API management SHALL keep domain modules profile-agnostic
The system SHALL keep `market`, `meta`, `formula`, `block`, and `runtime` domain modules independent from profile file loading and top-level profile merge logic.

#### Scenario: Runtime domain receives standardized parameters
- **WHEN** a runtime domain method is invoked by the manager
- **THEN** the domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

## ADDED Requirements

### Requirement: Query API management SHALL isolate runtime public query actions from market and meta domains
The system SHALL represent runtime public query actions through a dedicated `runtime` domain instead of placing them inside `market` or `meta`.

#### Scenario: Caller refreshes historical K-line cache through runtime domain
- **WHEN** a caller requests `refresh_kline` through the manager
- **THEN** the manager MUST expose that action through `manager.runtime.refresh_kline(...)`

#### Scenario: Caller requests trading dates or file download through runtime domain
- **WHEN** a caller requests `get_trading_dates` or `download_file` through the manager
- **THEN** the manager MUST expose those actions through `manager.runtime` rather than through `manager.market` or `manager.meta`
