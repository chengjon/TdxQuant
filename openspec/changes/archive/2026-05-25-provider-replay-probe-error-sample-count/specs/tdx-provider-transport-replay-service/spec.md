## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose error sample count

Provider replay status output SHALL include additive `runtime.probe_summary.error_sample_count` derived from the same probe results used for compact `error_samples`, without changing probe execution, daemon lifecycle, scheduler, restart, or provider mutation behavior.

#### Scenario: No requested probes have zero error sample count

- **WHEN** provider replay status is built without requested probes or probe errors
- **THEN** `runtime.probe_summary.error_sample_count` MUST be `0`
- **AND** the status call MUST remain read-only

#### Scenario: Error sample count includes all qualifying probe results

- **WHEN** provider replay status includes probe results that qualify for compact `error_samples`
- **THEN** `runtime.probe_summary.error_sample_count` MUST equal the total qualifying probe result count
- **AND** the count MUST NOT be capped by `runtime.probe_summary.error_sample_limit`
- **AND** `runtime.probe_summary.error_sample_truncated` MUST continue to indicate whether the sample list was truncated

#### Scenario: Summary view preserves error sample count

- **WHEN** a caller requests provider replay status with `--view summary`
- **THEN** the summary view MUST include `probe_summary.error_sample_count`
- **AND** the summary view MUST remain read-only and non-lifecycle-managing
