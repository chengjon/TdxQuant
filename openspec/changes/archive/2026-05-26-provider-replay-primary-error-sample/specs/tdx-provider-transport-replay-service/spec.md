# tdx-provider-transport-replay-service Spec Delta

## ADDED Requirements

### Requirement: Provider replay status SHALL expose primary error sample hints

Provider replay status SHALL include additive read-only `runtime.probe_summary.primary_error_sample_probe` and `runtime.probe_summary.primary_error_sample_status` derived from the existing bounded error sample list without requesting additional probes, exposing full probe payloads, starting sockets, mutating providers, scheduling retry/backoff, or managing daemon lifecycle.

#### Scenario: No error samples exist

- **GIVEN** provider replay status is built with no error samples
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.primary_error_sample_probe` MUST be `null`
- **AND** `runtime.probe_summary.primary_error_sample_status` MUST be `null`
- **AND** this field MUST NOT request or execute any probe

#### Scenario: Error samples exist

- **GIVEN** provider replay status is built with one or more error samples
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.primary_error_sample_probe` MUST equal the first sample probe
- **AND** `runtime.probe_summary.primary_error_sample_status` MUST equal the first sample status
- **AND** existing `error_samples`, `error_sample_count`, `error_sample_status_counts`, `error_sample_probe_counts`, and `error_sample_truncated` fields MUST remain available

#### Scenario: Primary error sample hints remain replay-only

- **WHEN** a caller inspects `runtime.probe_summary.primary_error_sample_probe` or `primary_error_sample_status`
- **THEN** these fields MUST NOT start sockets, mutate providers, schedule retry/backoff, request additional probes, or manage daemon lifecycle
- **AND** these fields MUST NOT be treated as provider readiness, endpoint coverage, or live TongDaXin runtime health proof
