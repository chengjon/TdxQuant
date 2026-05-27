## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose health summary

Provider replay status SHALL include additive read-only `runtime.probe_summary.health_summary` metadata derived from existing fixed-probe health fields without starting sockets, executing unrequested probes, managing daemon lifecycle, or enabling write behavior.

#### Scenario: Status includes no-probe health summary

- **WHEN** provider replay status is built without explicit probe requests
- **THEN** `runtime.probe_summary.health_summary.status` MUST be `not_requested`
- **AND** `healthy_count`, `failed_count`, and `unhealthy_count` MUST be `0`
- **AND** primary healthy/failed/unhealthy probe fields MUST be `null`
- **AND** existing probe summary sibling fields MUST remain available

#### Scenario: Status includes degraded health summary

- **WHEN** provider replay status is built with an unhealthy requested probe
- **THEN** `runtime.probe_summary.health_summary.status` MUST match `runtime.probe_summary.status`
- **AND** health/failure counts MUST match the corresponding sibling fields
- **AND** primary healthy/failed/unhealthy probe fields MUST match the corresponding sibling fields
- **AND** the object MUST NOT include full probe payloads, error samples, endpoint response bodies, daemon controls, or executable instructions

#### Scenario: Summary view exposes health summary without changing probe behavior

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** the summary view MUST expose `probe_summary.health_summary`
- **AND** the summary view MUST remain read-only and MUST NOT start sockets beyond explicitly requested probes, manage daemon lifecycle, or enable write behavior
