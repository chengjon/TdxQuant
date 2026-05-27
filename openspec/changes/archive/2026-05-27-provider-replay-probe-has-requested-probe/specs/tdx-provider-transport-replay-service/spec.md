## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose requested probe presence

Provider replay status SHALL include additive read-only top-level `runtime.probe_summary.has_requested_probe` derived only from existing normalized probe request metadata.

#### Scenario: No requested probes report false

- **WHEN** provider replay status has no requested probes
- **THEN** `runtime.probe_summary.has_requested_probe` MUST be `false`
- **AND** the field MUST remain consistent with `requested_count == 0`

#### Scenario: Requested probes report true

- **WHEN** provider replay status has one or more requested probes
- **THEN** `runtime.probe_summary.has_requested_probe` MUST be `true`
- **AND** the field MUST remain consistent with `requested_count > 0`

#### Scenario: Requested probe presence remains advisory

- **WHEN** provider replay status exposes `runtime.probe_summary.has_requested_probe`
- **THEN** the field MUST NOT indicate broker readiness, provider readiness, endpoint health, endpoint semantic coverage, daemon lifecycle control, or write capability
- **AND** the field MUST NOT indicate that an additional probe, provider mutation, socket start, restart/backoff, scheduler action, or write behavior was executed
