## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose failed HTTP status counts

Provider replay status output SHALL include additive `runtime.probe_summary.failed_http_status_counts` derived from requested non-healthy probe HTTP statuses without changing probe execution, daemon lifecycle, scheduler, restart, or provider mutation behavior.

#### Scenario: No requested probes have no failed HTTP status counts

- **WHEN** provider replay status is built without requested probes
- **THEN** `runtime.probe_summary.failed_http_status_counts` MUST be an empty object

#### Scenario: Non-healthy probe HTTP statuses are counted

- **WHEN** provider replay status includes requested probes with non-healthy status and integer HTTP statuses
- **THEN** `runtime.probe_summary.failed_http_status_counts` MUST count those HTTP status values as string keys
- **AND** the counts MUST exclude not-requested probes and healthy probes

#### Scenario: Summary view preserves failed HTTP status counts

- **WHEN** a caller requests provider replay status with `--view summary`
- **THEN** the summary view MUST include `probe_summary.failed_http_status_counts`
- **AND** the summary view MUST remain read-only and non-lifecycle-managing
