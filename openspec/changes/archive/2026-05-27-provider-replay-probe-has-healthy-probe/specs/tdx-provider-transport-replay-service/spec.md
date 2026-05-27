## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose healthy probe presence

Provider replay status SHALL include additive read-only `runtime.probe_summary.has_healthy_probe` derived only from existing normalized probe summary metadata.

#### Scenario: No healthy probes report false

- **WHEN** provider replay status has no healthy probes
- **THEN** `runtime.probe_summary.has_healthy_probe` MUST be `false`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Healthy probes report true

- **WHEN** provider replay status has one or more healthy probes
- **THEN** `runtime.probe_summary.has_healthy_probe` MUST be `true`
- **AND** the field MUST remain consistent with `healthy_count > 0`

#### Scenario: Healthy probe presence remains advisory

- **WHEN** provider replay status exposes `runtime.probe_summary.has_healthy_probe`
- **THEN** the field MUST NOT indicate broker readiness, provider readiness, endpoint coverage, daemon lifecycle control, or write capability
- **AND** the field MUST NOT indicate that an additional probe, provider mutation, socket start, restart/backoff, scheduler action, or write behavior was executed
