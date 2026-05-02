# tdx-provider-replay-fixtures Specification

## Purpose
TBD - created by archiving change add-provider-replay-fixtures. Update Purpose after archive.
## Requirements
### Requirement: Provider replay fixtures SHALL provide a stable built-in fixture bundle
The system SHALL provide a stable built-in replay fixture bundle for the current high-value provider-facing contracts so callers can validate integrations without live Windows runtime access.

#### Scenario: Consumer enumerates bundled replay fixtures
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the system MUST expose stable fixture names, capability identifiers, file formats, and descriptions for the bundled samples
- **AND** the synchronous JSON fixture catalog MUST include representative hardened-envelope snapshots for success and failure query/formula responses plus discovery fixtures for `runtime.capabilities`, `runtime.health`, and `runtime.doctor`
- **AND** the discovery fixture catalog MUST preserve representative hardened snapshots for capability registry, health, and doctor payloads

### Requirement: Provider replay fixtures SHALL support both JSON and JSONL contracts
The system SHALL support bundled replay samples for synchronous provider JSON responses and asynchronous provider event-row JSONL streams.

#### Scenario: Consumer loads a JSON replay fixture
- **WHEN** a caller loads a bundled synchronous provider fixture
- **THEN** the system MUST return a parsed JSON object that matches the packaged sample
- **AND** the returned JSON MUST preserve the hardened synchronous provider envelope, including the `success` / `ok` compatibility pair
- **AND** discovery fixtures MUST preserve the stabilized discovery payload fields, including structured action rows where applicable

#### Scenario: Consumer loads a JSONL replay fixture
- **WHEN** a caller loads a bundled provider event fixture
- **THEN** the system MUST return parsed rows in source order without requiring the caller to split lines manually

### Requirement: Provider replay fixtures SHALL remain independent from live runtime execution
The system SHALL keep the replay fixture bundle usable without TongDaXin runtime initialization, live probes, or live Windows-only dependencies.

#### Scenario: Consumer uses fixture loader without live runtime
- **WHEN** a caller loads a replay fixture on a machine without TongDaXin runtime access
- **THEN** the loader MUST still work because it depends only on packaged local assets
