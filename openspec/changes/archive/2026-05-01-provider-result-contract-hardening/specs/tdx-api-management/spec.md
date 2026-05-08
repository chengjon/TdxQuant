## MODIFIED Requirements

### Requirement: Query API management SHALL attach standardized management metadata
The system SHALL return manager-driven synchronous query and formula style results inside the provider-facing result envelope and SHALL attach standardized management metadata, including effective profile identity, timing fields, capability identity, schema/version metadata, and compatibility fields required by the current provider contract.

#### Scenario: Manager-driven query returns profile metadata in the provider result envelope
- **WHEN** a manager-driven query or formula style call completes
- **THEN** the result MUST include the effective API profile information used for the call within the provider-facing result envelope

#### Scenario: Manager-driven query returns timing fields in the provider result envelope
- **WHEN** a manager-driven query or formula style call completes
- **THEN** the result MUST include `started_at`, `finished_at`, and `elapsed_ms` fields for the manager-managed execution flow

#### Scenario: Manager-driven query returns capability identity and version metadata
- **WHEN** a manager-driven query or formula style call completes
- **THEN** the result MUST include `capability`, `capability_version`, and `schema_version` fields in addition to the manager metadata already attached by the manager layer

#### Scenario: Manager-driven query uses the hardened provider envelope
- **WHEN** a manager-driven query or formula style call completes
- **THEN** the result MUST include both `success` and `ok`
- **AND** the result MUST include a normalized `runtime` object
- **AND** the result MUST normalize `warnings` and `artifacts` as arrays and `data` as an object

### Requirement: Query API management SHALL attach standardized metadata to provider discovery responses
The system SHALL attach the same manager-driven metadata model to provider discovery style responses that it uses for other synchronous provider-facing capabilities.

#### Scenario: Manager capability discovery returns provider metadata
- **WHEN** a caller invokes `manager.runtime.capabilities(...)`, `manager.runtime.health(...)`, or `manager.runtime.doctor(...)`
- **THEN** the manager MUST attach effective profile metadata, capability identity, capability version, schema version, and timing metadata to the returned provider result envelope
- **AND** the returned envelope MUST include the same `success` / `ok` compatibility fields and normalized top-level container types that manager-driven query and formula calls use
