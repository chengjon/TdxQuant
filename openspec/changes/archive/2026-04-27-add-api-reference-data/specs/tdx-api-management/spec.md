## MODIFIED Requirements

### Requirement: Query API management SHALL provide a unified manager entrypoint
The system SHALL provide a `TdxApiManager` entrypoint for query-oriented TdxQuant capabilities so that callers do not need to invoke bridge functions directly for daily API workflows.

#### Scenario: Code caller uses manager to access meta reference data
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke dividend-factor and IPO reference data queries through `manager.meta.<method>()`

### Requirement: Query API management SHALL keep domain modules profile-agnostic
The system SHALL keep `market`, `meta`, `formula`, `block`, and `runtime` domain modules independent from profile file loading and top-level profile merge logic.

#### Scenario: Meta reference data method receives standardized parameters
- **WHEN** a meta reference data method is invoked by the manager
- **THEN** the domain method MUST accept explicit standardized parameters and delegate to `bridge.py` without reading profile files directly
