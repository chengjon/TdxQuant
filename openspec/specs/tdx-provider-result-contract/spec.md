# tdx-provider-result-contract Specification

## Purpose
TBD - created by archiving change add-provider-result-contract. Update Purpose after archive.
## Requirements
### Requirement: Provider result contract SHALL define a canonical synchronous result envelope
The system SHALL expose machine-readable synchronous provider results through a canonical JSON envelope with fixed top-level fields: `success`, `code`, `message`, `capability`, `capability_version`, `schema_version`, `request_id`, `started_at`, `finished_at`, `elapsed_ms`, `runtime`, `warnings`, `data`, and `artifacts`.

#### Scenario: Successful synchronous query, formula, or provider discovery result uses canonical envelope
- **WHEN** a synchronous provider-facing query, formula, or discovery style call completes successfully
- **THEN** the returned JSON MUST include the canonical top-level fields
- **AND** the `runtime` object MUST include provider identity, provider version, and execution mode metadata
- **AND** the `warnings` and `artifacts` fields MUST be present as arrays even when empty

### Requirement: Provider result contract SHALL preserve machine-readable failure semantics
The system SHALL use the same canonical JSON envelope for synchronous failures so that callers do not need to parse human-readable text to detect or classify errors.

#### Scenario: Failed synchronous query, formula, or provider discovery result uses canonical envelope
- **WHEN** a synchronous provider-facing query, formula, or discovery style call fails
- **THEN** the returned JSON MUST still use the canonical top-level fields
- **AND** `success` MUST be `false`
- **AND** `code` MUST contain a stable machine-readable failure code
- **AND** `message` MUST contain a human-readable summary without becoming the only source of failure semantics

### Requirement: Provider result contract SHALL separate common envelope fields from capability-specific payloads
The system SHALL keep common provider metadata in the top-level envelope and SHALL place capability-specific result content under `data` while reserving `artifacts` for external files or exported side products.

#### Scenario: Query, formula, or discovery payload remains inside data
- **WHEN** a synchronous provider-facing capability returns business data
- **THEN** the capability-specific payload MUST be placed under `data`
- **AND** top-level envelope fields MUST remain reserved for common provider metadata
- **AND** external file paths or exported outputs MUST be listed under `artifacts` rather than embedded into `data` as opaque strings

### Requirement: Provider result contract SHALL standardize common field formats
The system SHALL standardize common synchronous result field formats so that cross-language consumers can parse provider results consistently.

#### Scenario: Common result fields use stable formats
- **WHEN** a synchronous provider-facing query, formula, or discovery result includes timestamps, symbols, or enums
- **THEN** timestamps MUST use RFC3339 strings
- **AND** symbols MUST be represented as strings rather than numeric values
- **AND** enums MUST use fixed literal values instead of free-form human text

