## ADDED Requirements

### Requirement: Query API management SHALL expose provider discovery actions through the runtime domain
The system SHALL expose provider capability discovery, provider health, and provider doctor actions through the existing `runtime` domain on `TdxApiManager` instead of creating an unrelated top-level manager surface.

#### Scenario: Caller requests capability discovery through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke provider capability discovery through `manager.runtime.capabilities(...)`

#### Scenario: Caller requests provider diagnostics through manager
- **WHEN** a caller constructs `TdxApiManager`
- **THEN** the caller MUST be able to invoke provider health and doctor diagnostics through `manager.runtime.health(...)` and `manager.runtime.doctor(...)`

### Requirement: Query API management SHALL attach standardized metadata to provider discovery responses
The system SHALL attach the same manager-driven metadata model to provider discovery style responses that it uses for other synchronous provider-facing capabilities.

#### Scenario: Manager capability discovery returns provider metadata
- **WHEN** a caller invokes `manager.runtime.capabilities(...)`, `manager.runtime.health(...)`, or `manager.runtime.doctor(...)`
- **THEN** the manager MUST attach effective profile metadata, capability identity, capability version, schema version, and timing metadata to the returned provider result envelope
