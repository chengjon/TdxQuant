## MODIFIED Requirements

### Requirement: Query API management SHALL provide a unified manager entrypoint
The system SHALL provide a `TdxApiManager` entrypoint for query-oriented TdxQuant capabilities so that callers do not need to invoke bridge functions directly for daily API workflows.

#### Scenario: Code caller uses manager to access market kline query
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke K-line query capabilities through `manager.market.kline(...)`

#### Scenario: Code caller uses manager to access market full-tick query
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke full-tick query capabilities through `manager.market.full_tick(...)`

#### Scenario: Code caller uses manager to access formula domain
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke formula-related capabilities through `manager.formula.<method>()`

#### Scenario: Code caller uses manager to access block domain
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke block-related capabilities through `manager.block.<method>()`

### Requirement: Query API management SHALL keep domain modules profile-agnostic
The system SHALL keep `market`, `meta`, `formula`, and `block` domain modules independent from profile file loading and top-level profile merge logic.

#### Scenario: Market kline query receives standardized parameters
- **WHEN** a market K-line method is invoked by the manager
- **THEN** the domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

#### Scenario: Market full-tick query receives standardized field filters
- **WHEN** a market full-tick method is invoked by the manager
- **THEN** the domain method MUST accept explicit field filter parameters and delegate to `bridge.py` without reading profile files directly

#### Scenario: Formula domain receives standardized parameters
- **WHEN** a formula domain method is invoked by the manager
- **THEN** the domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly

#### Scenario: Block domain receives standardized parameters
- **WHEN** a block domain method is invoked by the manager
- **THEN** the domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly
