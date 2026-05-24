## ADDED Requirements

### Requirement: Provider replay status SHALL expose probe total count

Provider replay status SHALL include an additive read-only `runtime.probe_summary.total_count` scalar derived from the fixed supported probe key list without adding probe targets, requesting probes, starting sockets, or changing daemon lifecycle semantics.

#### Scenario: Detailed status includes total supported probe count

- **WHEN** a caller builds provider replay status
- **THEN** `runtime.probe_summary.total_count` MUST equal the number of supported provider replay status probes
- **AND** `runtime.probe_summary.requested_count + runtime.probe_summary.not_requested_count` MUST equal `runtime.probe_summary.total_count`
- **AND** the individual probe objects MUST remain present

#### Scenario: Summary view preserves total supported probe count

- **WHEN** a caller runs `provider-replay status --config <path> --view summary`
- **THEN** `summary_view.probe_summary.total_count` MUST match the detailed `runtime.probe_summary.total_count`
- **AND** the summary view MUST remain read-only projection data
- **AND** the command MUST NOT start, stop, restart, supervise, or schedule a replay service
