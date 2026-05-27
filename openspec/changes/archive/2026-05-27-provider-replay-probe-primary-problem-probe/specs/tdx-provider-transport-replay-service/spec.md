## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose primary problem probe

Provider replay status SHALL include additive read-only `runtime.probe_summary.primary_problem_probe` derived only from normalized fixed-probe summary metadata.

#### Scenario: No-probe status reports no primary problem probe

- **WHEN** provider replay status is built without requested probes
- **THEN** `runtime.probe_summary.primary_problem_probe` MUST be `null`
- **AND** `runtime.probe_summary.outcome_summary.primary_problem_probe` MUST also be `null`

#### Scenario: Degraded status reports first problem probe

- **WHEN** provider replay status includes a failed or unhealthy requested probe
- **THEN** `runtime.probe_summary.primary_problem_probe` MUST name the first failed probe when present
- **AND** it MUST match `runtime.probe_summary.outcome_summary.primary_problem_probe`

#### Scenario: Primary problem probe remains advisory

- **WHEN** provider replay status exposes `runtime.probe_summary.primary_problem_probe`
- **THEN** the field MUST NOT indicate that an additional probe, provider mutation, socket start, daemon lifecycle action, restart/backoff, scheduler action, or write behavior was executed
- **AND** the field MUST NOT claim broker readiness, provider readiness, endpoint coverage, or production daemon control
