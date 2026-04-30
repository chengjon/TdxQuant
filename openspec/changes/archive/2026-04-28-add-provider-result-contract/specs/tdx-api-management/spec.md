## MODIFIED Requirements

### Requirement: Query API management SHALL attach standardized management metadata
The system SHALL return manager-driven synchronous query and formula style results inside the provider-facing result envelope and SHALL attach standardized management metadata, including effective profile identity, timing fields, capability identity, and schema/version metadata.

#### Scenario: Manager-driven query returns profile metadata in the provider result envelope
- **WHEN** a manager-driven query or formula style call completes
- **THEN** the result MUST include the effective API profile information used for the call within the provider-facing result envelope

#### Scenario: Manager-driven query returns timing fields in the provider result envelope
- **WHEN** a manager-driven query or formula style call completes
- **THEN** the result MUST include `started_at`, `finished_at`, and `elapsed_ms` fields for the manager-managed execution flow

#### Scenario: Manager-driven query returns capability identity and version metadata
- **WHEN** a manager-driven query or formula style call completes
- **THEN** the result MUST include `capability`, `capability_version`, and `schema_version` fields in addition to the manager metadata already attached by the manager layer
