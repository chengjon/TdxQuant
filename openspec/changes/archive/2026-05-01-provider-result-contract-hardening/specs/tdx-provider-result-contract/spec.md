## ADDED Requirements

### Requirement: Provider result contract SHALL preserve a temporary `ok` compatibility alias
The system SHALL preserve a temporary top-level `ok` field as a compatibility alias of `success` for synchronous provider-facing JSON results during the current transition period.

#### Scenario: Compatibility alias mirrors canonical success field
- **WHEN** a synchronous provider-facing result is serialized
- **THEN** the top-level JSON MUST include both `success` and `ok`
- **AND** `ok` MUST be identical to `success`
- **AND** `success` MUST remain the canonical field documented for new integrations

## MODIFIED Requirements

### Requirement: Provider result contract SHALL define a canonical synchronous result envelope
The system SHALL expose machine-readable synchronous provider results through a canonical JSON envelope with fixed top-level fields: `success`, `ok`, `code`, `message`, `capability`, `capability_version`, `schema_version`, `request_id`, `started_at`, `finished_at`, `elapsed_ms`, `runtime`, `warnings`, `data`, and `artifacts`.

#### Scenario: Successful synchronous query, formula, or provider discovery result uses canonical envelope
- **WHEN** a synchronous provider-facing query, formula, or discovery style call completes successfully
- **THEN** the returned JSON MUST include the canonical top-level fields
- **AND** the `runtime` object MUST include provider identity, provider version, and execution mode metadata
- **AND** the `warnings` and `artifacts` fields MUST be present as arrays even when empty
- **AND** the `data` field MUST be present as an object even when no capability-specific payload members are present

### Requirement: Provider result contract SHALL preserve machine-readable failure semantics
The system SHALL use the same canonical JSON envelope for synchronous failures so that callers do not need to parse human-readable text to detect or classify errors.

#### Scenario: Failed synchronous query, formula, or provider discovery result uses canonical envelope
- **WHEN** a synchronous provider-facing query, formula, or discovery style call fails
- **THEN** the returned JSON MUST still use the canonical top-level fields
- **AND** `success` MUST be `false`
- **AND** `ok` MUST also be `false`
- **AND** `code` MUST contain a stable machine-readable failure code
- **AND** `message` MUST contain a human-readable summary without becoming the only source of failure semantics

#### Scenario: CLI provider failure keeps the canonical envelope
- **WHEN** a CLI command emits a synchronous provider-facing failure result
- **THEN** the command MUST still print the canonical JSON envelope
- **AND** the command MUST preserve a non-zero process exit code for the failed provider call

### Requirement: Provider result contract SHALL separate common envelope fields from capability-specific payloads
The system SHALL keep common provider metadata in the top-level envelope and SHALL place capability-specific result content under `data` while reserving `artifacts` for external files or exported side products.

#### Scenario: Query, formula, or discovery payload remains inside data
- **WHEN** a synchronous provider-facing capability returns business data
- **THEN** the capability-specific payload MUST be placed under `data`
- **AND** top-level envelope fields MUST remain reserved for common provider metadata
- **AND** external file paths or exported outputs MUST be listed under `artifacts` rather than embedded into `data` as opaque strings

#### Scenario: Legacy next-action guidance remains nested under data
- **WHEN** a synchronous provider-facing capability still needs to expose compatibility guidance such as `next_action`
- **THEN** that compatibility payload MUST remain under `data`
- **AND** the top-level envelope MUST NOT reintroduce `next_action` as a canonical top-level field

### Requirement: Provider result contract SHALL standardize common field formats
The system SHALL standardize common synchronous result field formats so that cross-language consumers can parse provider results consistently.

#### Scenario: Common result fields use stable formats
- **WHEN** a synchronous provider-facing query, formula, or discovery result includes timestamps, symbols, enums, or timing values
- **THEN** timestamps MUST use RFC3339 strings
- **AND** symbols MUST be represented as strings rather than numeric values
- **AND** enums MUST use fixed literal values instead of free-form human text
- **AND** `elapsed_ms` MUST use a numeric JSON value
