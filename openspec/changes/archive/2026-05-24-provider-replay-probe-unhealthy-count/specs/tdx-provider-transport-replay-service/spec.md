## ADDED Requirements

### Requirement: Provider replay status SHALL expose unhealthy probe count

Provider replay status SHALL include an additive read-only `runtime.probe_summary.unhealthy_count` scalar derived from existing probe status rollup data without adding probe targets, requesting probes, starting sockets, or changing daemon lifecycle semantics.

#### Scenario: Detailed status includes unhealthy probe count

- **WHEN** a caller builds provider replay status
- **THEN** `runtime.probe_summary.unhealthy_count` MUST equal the number of entries in `runtime.probe_summary.unhealthy`
- **AND** `runtime.probe_summary.unhealthy_count` MUST equal `runtime.probe_summary.failed_count`
- **AND** the individual probe objects MUST remain present

#### Scenario: Summary view preserves unhealthy probe count

- **WHEN** a caller requests provider replay status with `--view summary`
- **THEN** `summary_view.probe_summary.unhealthy_count` MUST equal the detailed `runtime.probe_summary.unhealthy_count`
- **AND** the summary view MUST remain a read-only projection
