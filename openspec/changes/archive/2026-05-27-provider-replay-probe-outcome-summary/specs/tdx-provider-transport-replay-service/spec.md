## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose outcome summary

Provider replay status SHALL include additive read-only `runtime.probe_summary.outcome_summary` metadata derived from existing fixed-probe summary fields without starting sockets, executing unrequested probes, changing health classification, managing daemon lifecycle, or enabling write behavior.

#### Scenario: Status includes no-probe outcome summary

- **WHEN** provider replay status is built without explicit probe requests
- **THEN** `runtime.probe_summary.outcome_summary.status` MUST be `not_requested`
- **AND** `request_coverage_status` MUST be `none`
- **AND** `all_probes_requested`, `has_failed_probe`, and `has_unhealthy_probe` MUST be `false`
- **AND** `primary_problem_probe`, `primary_error_sample_probe`, and `primary_error_sample_status` MUST be `null`
- **AND** existing probe summary sibling fields MUST remain available

#### Scenario: Status includes degraded outcome summary

- **WHEN** provider replay status is built with at least one failed or unhealthy requested probe
- **THEN** `runtime.probe_summary.outcome_summary.status` MUST match the existing probe summary status
- **AND** `request_coverage_status` MUST match the existing request coverage status
- **AND** `has_failed_probe` and `has_unhealthy_probe` MUST reflect existing failed and unhealthy counts
- **AND** `primary_problem_probe` MUST identify the first failed, unhealthy, or primary error-sample probe already present in the existing summary

#### Scenario: Summary view exposes outcome summary without changing probe behavior

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** the summary view MUST expose `probe_summary.outcome_summary`
- **AND** the summary view MUST remain read-only and MUST NOT start sockets beyond explicitly requested probes, manage daemon lifecycle, or enable write behavior
