# tdx-provider-transport-replay-service Spec Delta

## ADDED Requirements

### Requirement: Provider replay status SHALL expose primary error sample diagnostics

Provider replay status SHALL include additive read-only `runtime.probe_summary.primary_error_sample_error_code` and `runtime.probe_summary.primary_error_sample_http_status` derived from the existing bounded error sample list without requesting additional probes, exposing full probe payloads, starting sockets, mutating providers, scheduling retry/backoff, or managing daemon lifecycle.

#### Scenario: No error samples exist

- **GIVEN** provider replay status is built with no error samples
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.primary_error_sample_error_code` MUST be `null`
- **AND** `runtime.probe_summary.primary_error_sample_http_status` MUST be `null`
- **AND** these fields MUST NOT request or execute any probe

#### Scenario: Error samples include compact diagnostics

- **GIVEN** provider replay status is built with one or more error samples that include compact diagnostic fields
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.primary_error_sample_error_code` MUST equal the first sample error code when present
- **AND** `runtime.probe_summary.primary_error_sample_http_status` MUST equal the first sample HTTP status when present
- **AND** existing `error_samples`, `primary_error_sample_probe`, `primary_error_sample_status`, and error sample count fields MUST remain available

#### Scenario: Primary error sample diagnostics remain replay-only

- **WHEN** a caller inspects `runtime.probe_summary.primary_error_sample_error_code` or `primary_error_sample_http_status`
- **THEN** these fields MUST NOT start sockets, mutate providers, schedule retry/backoff, request additional probes, or manage daemon lifecycle
- **AND** these fields MUST NOT be treated as provider readiness, endpoint coverage, or live TongDaXin runtime health proof
