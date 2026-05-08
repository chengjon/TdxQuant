## ADDED Requirements

### Requirement: Query API management SHALL preserve hardened query metadata across manager-driven query domains
The system SHALL expose the stabilized query metadata contract for `market`, `meta`, `financial`, and `transaction` manager calls in addition to the existing provider result envelope.

#### Scenario: Manager-driven market query returns hardened query metadata
- **WHEN** a caller executes a manager-driven market query
- **THEN** the returned result MUST include the standardized query metadata under `data.query_meta` required by the provider query contract

#### Scenario: Manager-driven meta query returns hardened query metadata
- **WHEN** a caller executes a manager-driven meta query
- **THEN** the returned result MUST include the standardized query metadata under `data.query_meta` required by the provider query contract

#### Scenario: Manager-driven financial or transaction query returns hardened query metadata
- **WHEN** a caller executes a manager-driven financial or transaction query
- **THEN** the returned result MUST include the standardized query metadata under `data.query_meta` required by the provider query contract

#### Scenario: Manager layer preserves effective requested-field semantics
- **WHEN** a covered manager query resolves field defaults or normalized explicit field lists before calling the provider
- **THEN** `data.query_meta.requested_fields` MUST reflect that effective provider-bound field list rather than the caller's raw pre-normalization input

### Requirement: Query API management SHALL keep replay-mode query results contract-equivalent to live results
The system SHALL preserve the same hardened query metadata shape when a covered query capability is resolved from replay fixtures instead of live runtime execution.

#### Scenario: Replay-mode manager query preserves query metadata contract
- **WHEN** a caller executes a covered manager query in `provider_mode=replay`
- **THEN** the returned result MUST preserve the same `data.query_meta` fields and selector semantics as the live contract for that capability
