## ADDED Requirements

### Requirement: Provider subscription event rows SHALL expose additive reconnect metadata
The system SHALL keep `reconnect_metadata` as a stable object field and MAY populate it with additive reconnect context when a subscription event is observed after reconnect or degraded transitions.

#### Scenario: Event row without reconnect context remains compatible
- **WHEN** a subscription event row is emitted without reconnect-specific context
- **THEN** `reconnect_metadata` MUST remain present
- **AND** it MAY be an empty object

#### Scenario: Event row after reconnect includes additive reconnect context
- **WHEN** a subscription event row is emitted after a reconnect or degraded recovery
- **THEN** `reconnect_metadata` MAY include `reconnect_count`, `session_generation`, `last_disconnect_at`, `last_reconnect_at`, and `degraded_since`
- **AND** consumers MUST NOT be required to treat those additive fields as transport-specific metadata

#### Scenario: Transport frame does not rewrite the event-row schema
- **WHEN** a subscription event row is delivered through a stream transport frame
- **THEN** the normalized event row MUST remain under the frame payload's `event` field
- **AND** stream-only fields such as cursor, transport name, heartbeat, or terminal status MUST remain outside the normalized event row

