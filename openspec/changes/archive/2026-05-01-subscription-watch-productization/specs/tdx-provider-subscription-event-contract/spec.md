## MODIFIED Requirements

### Requirement: Provider subscription updates SHALL expose a stable normalized event-row contract
The system SHALL define a stable provider-facing event-row contract for TongDaXin subscription quote updates so upstream consumers can rely on a transport-independent schema instead of task-local or callback-local shapes.

#### Scenario: Consumer reads a normalized subscription event row
- **WHEN** a normalized subscription update row is emitted by the provider-facing subscription workflow
- **THEN** the row MUST include `schema_version`, `capability`, `run_id`, `session_id`, `provider_instance_id`, `subscription_id`, `sequence`, `event_type`, `symbol`, `source_ts`, `event_ts`, `reconnect_metadata`, and `payload`
- **AND** `reconnect_metadata` MUST remain present even when the row has no reconnect-specific fields to report
