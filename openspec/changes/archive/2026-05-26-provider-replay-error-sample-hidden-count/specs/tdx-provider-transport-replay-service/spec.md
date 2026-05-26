# tdx-provider-transport-replay-service Spec Delta

## ADDED Requirements

### Requirement: Provider replay status SHALL expose hidden error sample count

Provider replay status SHALL include additive read-only `runtime.probe_summary.error_sample_hidden_count` derived from the existing bounded error sample list and total error sample candidate count without requesting additional probes, exposing full probe payloads, starting sockets, mutating providers, scheduling retry/backoff, or managing daemon lifecycle.

#### Scenario: No error samples are hidden

- **GIVEN** provider replay status is built with zero error samples or with sample candidates within the configured sample limit
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.error_sample_hidden_count` MUST be `0`
- **AND** existing `error_sample_count`, `error_sample_limit`, and `error_sample_truncated` fields MUST remain unchanged

#### Scenario: Error sample candidates are truncated

- **GIVEN** provider replay status is built with more error sample candidates than the configured sample limit
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.error_sample_hidden_count` MUST equal `error_sample_count - len(error_samples)`
- **AND** `runtime.probe_summary.error_sample_truncated` MUST remain `true`

#### Scenario: Hidden error sample count remains replay-only

- **WHEN** a caller inspects `runtime.probe_summary.error_sample_hidden_count`
- **THEN** this field MUST NOT start sockets, mutate providers, schedule retry/backoff, request additional probes, or manage daemon lifecycle
- **AND** this field MUST NOT be treated as provider readiness, endpoint coverage, or live TongDaXin runtime health proof
