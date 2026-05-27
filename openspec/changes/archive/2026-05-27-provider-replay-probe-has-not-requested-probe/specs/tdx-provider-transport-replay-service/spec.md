## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose not-requested probe presence

Provider replay status SHALL include additive read-only `runtime.probe_summary.has_not_requested_probe` derived only from existing normalized probe request coverage metadata.

#### Scenario: No not-requested probes report false

- **WHEN** provider replay status has no configured probes or all configured probes were requested
- **THEN** `runtime.probe_summary.has_not_requested_probe` MUST be `false`
- **AND** the field MUST remain consistent with `not_requested_count == 0`

#### Scenario: Not-requested probes report true

- **WHEN** provider replay status has one or more configured probes that were not requested
- **THEN** `runtime.probe_summary.has_not_requested_probe` MUST be `true`
- **AND** the field MUST remain consistent with `not_requested_count > 0`

#### Scenario: Not-requested probe presence remains advisory

- **WHEN** provider replay status exposes `runtime.probe_summary.has_not_requested_probe`
- **THEN** the field MUST NOT indicate provider failure, broker readiness, provider readiness, endpoint coverage, daemon lifecycle control, or write capability
- **AND** the field MUST NOT indicate that an additional probe, provider mutation, socket start, restart/backoff, scheduler action, or write behavior was executed
