## ADDED Requirements

### Requirement: Provider replay fixtures SHALL include delayed transport playback samples
The system SHALL provide representative replay fixtures that describe delayed playback behavior for provider transport streams.

#### Scenario: Fixture catalog includes delayed playback sample
- **WHEN** a caller enumerates the built-in provider replay fixture catalog
- **THEN** the catalog MUST include a delayed playback transport sample
- **AND** the sample MUST be loadable without live runtime dependencies

#### Scenario: Delayed playback sample preserves canonical event-stream frame shape
- **WHEN** a caller loads the delayed playback transport sample
- **THEN** the sample MUST contain replay frame objects with JSON-compatible status, quote, heartbeat, or terminal frame payloads
- **AND** quote frames MUST include deterministic playback offset metadata

### Requirement: Provider replay fixture descriptors SHALL mark transport replay samples
The system SHALL distinguish transport replay fixtures from synchronous result fixtures and artifact replay fixtures.

#### Scenario: Transport replay descriptors include transport metadata
- **WHEN** a caller enumerates provider replay fixtures
- **THEN** transport replay fixtures MUST include descriptor metadata identifying their transport surface and playback mode
