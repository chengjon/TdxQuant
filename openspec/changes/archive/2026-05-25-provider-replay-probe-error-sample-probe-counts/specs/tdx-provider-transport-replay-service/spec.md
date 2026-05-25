## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose error sample probe counts

Provider replay status output SHALL include additive `runtime.probe_summary.error_sample_probe_counts` derived from the same probe results used for compact `error_samples`, without changing probe execution, daemon lifecycle, scheduler, restart, or provider mutation behavior.

#### Scenario: No error sample candidates have empty probe counts

- **WHEN** provider replay status is built without probe results that qualify for compact error samples
- **THEN** `runtime.probe_summary.error_sample_probe_counts` MUST be an empty object
- **AND** the status call MUST remain read-only

#### Scenario: Error sample candidates are counted by probe key

- **WHEN** provider replay status includes probe results that qualify for compact `error_samples`
- **THEN** `runtime.probe_summary.error_sample_probe_counts` MUST count those candidates by probe key
- **AND** the counts MUST use string probe keys
- **AND** the counts MUST NOT depend on whether `error_samples` is truncated

#### Scenario: Summary view preserves error sample probe counts

- **WHEN** a caller requests provider replay status with `--view summary`
- **THEN** the summary view MUST include `probe_summary.error_sample_probe_counts`
- **AND** the summary view MUST remain read-only and non-lifecycle-managing

