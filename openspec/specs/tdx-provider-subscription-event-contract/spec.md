# tdx-provider-subscription-event-contract Specification

## Purpose
TBD - created by archiving change add-provider-subscription-event-contract. Update Purpose after archive.
## Requirements
### Requirement: Provider subscription updates SHALL expose a stable normalized event-row contract
The system SHALL define a stable provider-facing event-row contract for TongDaXin subscription quote updates so upstream consumers can rely on a transport-independent schema instead of task-local or callback-local shapes.

#### Scenario: Consumer reads a normalized subscription event row
- **WHEN** a normalized subscription update row is emitted by the provider-facing subscription workflow
- **THEN** the row MUST include `schema_version`, `capability`, `run_id`, `session_id`, `provider_instance_id`, `subscription_id`, `sequence`, `event_type`, `symbol`, `source_ts`, `event_ts`, `reconnect_metadata`, and `payload`
- **AND** `reconnect_metadata` MUST remain present even when the row has no reconnect-specific fields to report

### Requirement: Provider subscription event rows SHALL preserve raw callback context
The system SHALL preserve the serialized raw callback context inside the normalized event row so consumers can inspect source payload details without depending on TongDaXin callback transport internals.

#### Scenario: Raw callback payload is preserved in normalized event row
- **WHEN** the provider normalizes a subscription callback payload into an event row
- **THEN** the normalized row MUST retain the serialized callback data in `payload`
- **AND** the provider MUST still attempt to extract stable `symbol` and `source_ts` fields when possible

### Requirement: Provider subscription event rows SHALL remain transport-independent
The system SHALL define subscription event rows independently from the foreground task or any future HTTP/SSE transport so the same schema can be reused across multiple delivery channels.

#### Scenario: Different delivery channels reuse the same event row schema
- **WHEN** the system emits subscription updates through a foreground task artifact or a future delivery channel
- **THEN** the normalized event row schema MUST remain the same even if the surrounding transport metadata differs

