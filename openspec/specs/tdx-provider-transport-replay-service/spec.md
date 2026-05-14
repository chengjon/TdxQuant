# tdx-provider-transport-replay-service Specification

## Purpose
TBD - created by archiving change provider-transport-replay-fixtures. Update Purpose after archive.
## Requirements
### Requirement: Provider transport replay service SHALL expose a fixture-backed HTTP surface
The system SHALL provide a small HTTP replay service that serves supported provider replay fixtures without live Windows runtime access.

#### Scenario: Replay service health reports replay-only mode
- **WHEN** a caller requests the replay service health endpoint with valid authorization
- **THEN** the service MUST return a successful machine-readable envelope
- **AND** the response MUST identify `provider_mode` as `replay`
- **AND** the response MUST NOT require TongDaXin runtime initialization

#### Scenario: Replay service exposes the built-in fixture catalog
- **WHEN** a caller requests the replay service fixture catalog
- **THEN** the service MUST return the same built-in fixture descriptors exposed by the replay fixture catalog helper
- **AND** each descriptor MUST preserve fixture name, capability, format, and relative path metadata

#### Scenario: Replay service serves a synchronous replay result
- **WHEN** a caller requests a supported synchronous capability through the replay service
- **THEN** the service MUST resolve the same default or explicit replay fixture as in-process replay mode
- **AND** the returned payload MUST preserve the provider result contract
- **AND** no live fallback MAY be attempted

### Requirement: Provider transport replay service SHALL simulate subscription-watch daemon read paths
The system SHALL expose read-only subscription-watch status, events, and event-stream endpoints backed by replay fixtures.

#### Scenario: Fake provider returns replay watch status
- **WHEN** a caller requests subscription-watch status from the replay service
- **THEN** the service MUST return replay fixture status projected as a daemon-backed watch status response
- **AND** the response MUST identify the source as replay fixture data

#### Scenario: Fake provider returns replay watch event rows
- **WHEN** a caller requests subscription-watch events from the replay service
- **THEN** the service MUST return replay fixture event rows in canonical subscription event shape
- **AND** the response MUST support a tail limit without changing the fixture source

#### Scenario: Fake provider streams replay watch frames
- **WHEN** a caller requests the subscription-watch replay event stream
- **THEN** the service MUST return Server-Sent Events frames with JSON `data` payloads
- **AND** the frames MUST include status, quote, heartbeat or terminal projections as appropriate for the fixture

### Requirement: Provider transport replay service SHALL support deterministic delayed playback metadata
The system SHALL allow replay stream callers to request delayed playback semantics without relying on live sleeps or nondeterministic timing.

#### Scenario: Delayed playback frames carry planned timing metadata
- **WHEN** a caller requests replay stream frames with delayed playback enabled
- **THEN** each emitted stream frame MUST include replay playback metadata
- **AND** quote frames MUST expose deterministic planned emit offsets derived from fixture order and requested delay

#### Scenario: Immediate playback remains the default
- **WHEN** a caller requests replay stream frames without delayed playback options
- **THEN** the service MUST emit frames in fixture order
- **AND** frame payloads MUST identify playback mode as `immediate`

### Requirement: Provider transport replay service SHALL enforce daemon-style access boundaries
The system SHALL protect the replay HTTP surface with the same minimal daemon access boundaries used by the bridge control plane.

#### Scenario: Replay service rejects missing or invalid bearer token
- **WHEN** a caller requests any replay HTTP endpoint without the configured bearer token
- **THEN** the service MUST reject the request with a machine-readable unauthorized error

#### Scenario: Replay service rejects disallowed source IP
- **WHEN** a caller requests any replay HTTP endpoint from a source outside the configured allowlist
- **THEN** the service MUST reject the request with a machine-readable forbidden-source error

