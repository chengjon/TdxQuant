## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose failed error-code counts

The provider replay status result SHALL include an additive `runtime.probe_summary.failed_error_code_counts` object derived from requested non-healthy probe error codes without starting sockets, adding probe endpoints, or managing daemon lifecycle.

#### Scenario: No requested probes have empty failed error-code counts

- **WHEN** provider replay status is built without requested probes
- **THEN** `runtime.probe_summary.failed_error_code_counts` MUST be an empty object
- **AND** `runtime.probe_summary.not_requested_count` MUST remain unchanged

#### Scenario: Failed requested probes have failed error-code counts

- **WHEN** a requested probe is non-healthy and includes a string `error_code`
- **THEN** `runtime.probe_summary.failed_error_code_counts` MUST count that error code
- **AND** healthy and `not_requested` probes MUST NOT contribute to failed error-code counts
- **AND** the rollup MUST remain a read-only summary

#### Scenario: Summary view preserves failed error-code counts

- **WHEN** a caller requests provider replay status with `--view summary`
- **THEN** the summary view MUST include `probe_summary.failed_error_code_counts`
- **AND** the summary view MUST remain a read-only projection
