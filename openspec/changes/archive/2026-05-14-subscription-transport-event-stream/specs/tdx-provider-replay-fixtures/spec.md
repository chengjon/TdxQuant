## ADDED Requirements

### Requirement: Provider replay fixtures SHALL include representative subscription event-stream transport samples
The system SHALL provide representative replay fixtures for the subscription event-stream transport so callers can validate stream parsing without live Windows runtime access.

#### Scenario: Fixture catalog includes subscription stream frame samples
- **WHEN** a caller enumerates the built-in provider replay fixture catalog
- **THEN** the catalog MUST include representative subscription event-stream samples
- **AND** the samples MUST cover quote, status, heartbeat, reconnecting, degraded, and terminal frame projections

#### Scenario: Stream fixture preserves canonical event rows inside frame payloads
- **WHEN** a caller loads a subscription event-stream replay fixture
- **THEN** quote frames MUST preserve the normalized subscription event row under the frame payload's `event` field
- **AND** transport fields MUST remain outside the normalized event row

#### Scenario: Stream fixture can be loaded without live runtime
- **WHEN** a caller loads subscription event-stream replay fixtures on a machine without TongDaXin runtime access
- **THEN** the loader MUST parse the samples from packaged local assets without live probes or Windows-only dependencies

