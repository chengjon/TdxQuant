## ADDED Requirements

### Requirement: Provider replay status SHALL expose a primary unhealthy probe hint

Provider replay status SHALL include additive `runtime.probe_summary.primary_unhealthy_probe` derived from the existing unhealthy probe list without requesting additional probes, changing health classification, starting sockets, mutating providers, scheduling retry/backoff, or managing daemon lifecycle.

#### Scenario: No unhealthy probes exist

- **GIVEN** provider replay status is built with no unhealthy probes
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.primary_unhealthy_probe` MUST be `null`
- **AND** this field MUST NOT request or execute any probe

#### Scenario: Unhealthy probes exist

- **GIVEN** provider replay status is built with one or more unhealthy probes
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.primary_unhealthy_probe` MUST equal the first item in `runtime.probe_summary.unhealthy`
- **AND** existing `unhealthy`, `unhealthy_count`, `failed`, and `primary_failed_probe` fields MUST remain available

#### Scenario: Primary unhealthy probe remains read-only

- **WHEN** a caller inspects provider replay status or summary view
- **THEN** `runtime.probe_summary.primary_unhealthy_probe` MUST NOT start sockets, mutate providers, schedule retry/backoff, or manage daemon lifecycle
- **AND** the field MUST NOT be treated as service health, readiness, endpoint coverage, or production daemon control proof

