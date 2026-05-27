## ADDED Requirements

### Requirement: Provider replay health summary SHALL expose probe presence flags

Provider replay status SHALL include additive read-only `runtime.probe_summary.health_summary.has_healthy_probe`, `has_failed_probe`, and `has_unhealthy_probe` fields derived only from existing normalized fixed-probe summary metadata.

#### Scenario: No-probe health summary reports no presence

- **WHEN** provider replay status is built without explicit probe requests
- **THEN** `runtime.probe_summary.health_summary.has_healthy_probe` MUST be `false`
- **AND** `runtime.probe_summary.health_summary.has_failed_probe` MUST be `false`
- **AND** `runtime.probe_summary.health_summary.has_unhealthy_probe` MUST be `false`
- **AND** no probe operation MUST be executed to compute those fields

#### Scenario: Degraded health summary reports failed and unhealthy presence

- **WHEN** provider replay status is built with an unhealthy requested probe
- **THEN** `runtime.probe_summary.health_summary.has_failed_probe` MUST be `true`
- **AND** `runtime.probe_summary.health_summary.has_unhealthy_probe` MUST be `true`
- **AND** each field MUST match the corresponding top-level `runtime.probe_summary` presence field
- **AND** the summary MUST NOT include full probe payloads, endpoint response bodies, daemon controls, or executable instructions

#### Scenario: Summary view exposes health presence flags without changing probe behavior

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** the summary view MUST expose the same `probe_summary.health_summary` presence flags
- **AND** the command MUST remain read-only and MUST NOT start sockets beyond explicitly requested probes, manage daemon lifecycle, schedule supervision, or enable write behavior

