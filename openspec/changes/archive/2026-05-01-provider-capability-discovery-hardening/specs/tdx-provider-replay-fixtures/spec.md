## MODIFIED Requirements

### Requirement: Provider replay fixtures SHALL provide a stable built-in fixture bundle
The system SHALL provide a stable built-in replay fixture bundle for the current high-value provider-facing contracts so callers can validate integrations without live Windows runtime access.

#### Scenario: Consumer enumerates bundled replay fixtures
- **WHEN** a caller requests the built-in provider replay fixture catalog
- **THEN** the system MUST expose stable fixture names, capability identifiers, file formats, and descriptions for the bundled samples
- **AND** the discovery fixture catalog MUST include representative hardened snapshots for capability registry, health, and doctor payloads

### Requirement: Provider replay fixtures SHALL support both JSON and JSONL contracts
The system SHALL support bundled replay samples for synchronous provider JSON responses and asynchronous provider event-row JSONL streams.

#### Scenario: Consumer loads a JSON replay fixture
- **WHEN** a caller loads a bundled synchronous provider fixture
- **THEN** the system MUST return a parsed JSON object that matches the packaged sample
- **AND** discovery fixtures MUST preserve the hardened provider envelope plus the stabilized discovery payload fields, including structured action rows where applicable

#### Scenario: Consumer loads a JSONL replay fixture
- **WHEN** a caller loads a bundled provider event fixture
- **THEN** the system MUST return parsed rows in source order without requiring the caller to split lines manually
