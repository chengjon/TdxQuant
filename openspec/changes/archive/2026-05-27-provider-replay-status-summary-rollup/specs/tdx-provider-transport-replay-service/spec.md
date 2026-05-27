## ADDED Requirements

### Requirement: Provider replay summary view SHALL expose status summary rollup

`provider-replay status --view summary` SHALL include additive read-only `summary_view.status_summary` metadata derived from the already-built provider replay status payload without starting services, executing extra probes, changing detailed status payloads, managing daemon lifecycle, or enabling write behavior.

#### Scenario: Summary view exposes stable replay status rollup

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.status_summary.provider_id` and `transport_mode` MUST match the provider replay status payload
- **AND** `source_kind`, `fixture`, `read_only`, `writes_supported`, `endpoint_count`, `probe_requested`, `requested_probe_count`, `failed_probe_count`, `control_supported`, `managed_operation_count`, `boundary_count`, `runtime_observed`, and `live_runtime_required` MUST be present
- **AND** the summary MUST be derived from existing status, capability, runtime, lifecycle, replay source, and boundary data

#### Scenario: Summary rollup remains read-only and non-authoritative

- **WHEN** the summary rollup is built
- **THEN** it MUST NOT execute probes beyond those explicitly requested by the caller
- **AND** it MUST NOT start, stop, restart, daemonize, schedule, supervise, or otherwise manage a provider process
- **AND** it MUST NOT expose bearer tokens, allowlist members, full endpoint lists, fixture paths, or write-capable controls
- **AND** it MUST NOT claim live provider readiness, production suitability, or workflow execution support
