## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose request summary

Provider replay status SHALL include additive read-only `runtime.probe_summary.request_summary` metadata derived from existing fixed-probe request coverage fields without starting sockets, executing unrequested probes, managing daemon lifecycle, or enabling write behavior.

#### Scenario: Status includes no-probe request summary

- **WHEN** provider replay status is built without explicit probe requests
- **THEN** `runtime.probe_summary.request_summary.status` MUST be `none`
- **AND** `requested_count` MUST be `0`
- **AND** `not_requested_count` MUST match the number of supported fixed probes
- **AND** `primary_not_requested_probe` MUST remain deterministic
- **AND** existing probe summary sibling fields MUST remain available

#### Scenario: Status includes complete request summary

- **WHEN** provider replay status is built with all fixed probes explicitly requested
- **THEN** `runtime.probe_summary.request_summary.status` MUST be `complete`
- **AND** `requested_count` MUST match `runtime.probe_summary.requested_count`
- **AND** `healthy_count`, `failed_count`, and `unhealthy_count` MUST match the corresponding sibling fields
- **AND** `primary_requested_probe` and `primary_not_requested_probe` MUST match the corresponding sibling fields
- **AND** the object MUST NOT include full probe payloads, error samples, endpoint response bodies, daemon controls, or executable instructions

#### Scenario: Summary view exposes request summary without changing probe behavior

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** the summary view MUST expose `probe_summary.request_summary`
- **AND** the summary view MUST remain read-only and MUST NOT start sockets beyond explicitly requested probes, manage daemon lifecycle, or enable write behavior
