## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose top-level unhealthy probe presence

Provider replay status SHALL include additive read-only top-level `runtime.probe_summary.has_unhealthy_probe` derived only from existing normalized unhealthy probe metadata.

#### Scenario: No unhealthy probes report false

- **WHEN** provider replay status has no unhealthy probes
- **THEN** top-level `runtime.probe_summary.has_unhealthy_probe` MUST be `false`
- **AND** the field MUST remain consistent with `unhealthy_count == 0`

#### Scenario: Unhealthy probes report true

- **WHEN** provider replay status has one or more unhealthy probes
- **THEN** top-level `runtime.probe_summary.has_unhealthy_probe` MUST be `true`
- **AND** the field MUST remain consistent with `unhealthy_count > 0`
- **AND** the field MUST match `outcome_summary.has_unhealthy_probe`

#### Scenario: Unhealthy probe presence remains advisory

- **WHEN** provider replay status exposes top-level `runtime.probe_summary.has_unhealthy_probe`
- **THEN** the field MUST NOT indicate broker readiness, provider readiness, endpoint semantic coverage, daemon lifecycle control, or write capability
- **AND** the field MUST NOT indicate that an additional probe, provider mutation, socket start, restart/backoff, scheduler action, or write behavior was executed
