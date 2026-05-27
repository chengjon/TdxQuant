## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose advisory summary

Provider replay status SHALL include additive read-only `runtime.probe_summary.advisory_summary` metadata derived only from existing normalized fixed-probe summary fields.

#### Scenario: No-probe status exposes an advisory summary

- **WHEN** provider replay status is built without explicit probe requests
- **THEN** `runtime.probe_summary.advisory_summary.status` MUST be `not_requested`
- **AND** `runtime.probe_summary.advisory_summary.request_coverage_status` MUST be `none`
- **AND** `runtime.probe_summary.advisory_summary.has_requested_probe` MUST be `false`
- **AND** `runtime.probe_summary.advisory_summary.has_problem_probe` MUST be `false`
- **AND** no probe operation MUST be executed to compute the advisory summary

#### Scenario: Degraded status exposes problem advisory hints

- **WHEN** provider replay status is built with an unhealthy requested probe
- **THEN** `runtime.probe_summary.advisory_summary.status` MUST match `runtime.probe_summary.status`
- **AND** the advisory counts and presence flags MUST match the corresponding sibling fields
- **AND** `runtime.probe_summary.advisory_summary.primary_problem_probe` MUST match the corresponding sibling field
- **AND** the advisory summary MUST include a read-only boundary marker
- **AND** the advisory summary MUST NOT include full probe payloads, endpoint response bodies, daemon controls, or executable instructions

#### Scenario: Summary view exposes advisory summary without changing probe behavior

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** the summary view MUST expose `probe_summary.advisory_summary`
- **AND** the command MUST remain read-only and MUST NOT start sockets beyond explicitly requested probes, manage daemon lifecycle, schedule supervision, or enable write behavior

