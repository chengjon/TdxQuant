# tdx-provider-transport-replay-service Spec Delta

## ADDED Requirements

### Requirement: Provider replay status SHALL expose visible error sample count

Provider replay status SHALL include additive read-only `runtime.probe_summary.error_sample_visible_count` derived from the existing bounded error sample list without requesting additional probes, exposing full probe payloads, starting sockets, mutating providers, scheduling retry/backoff, or managing daemon lifecycle.

#### Scenario: No error samples are visible

- **GIVEN** provider replay status is built with zero visible error samples
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.error_sample_visible_count` MUST be `0`
- **AND** existing `error_sample_count`, `error_sample_hidden_count`, `error_sample_limit`, and `error_sample_truncated` fields MUST remain unchanged

#### Scenario: Error samples are visible

- **GIVEN** provider replay status is built with one or more visible bounded error samples
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.error_sample_visible_count` MUST equal `len(error_samples)`
- **AND** `runtime.probe_summary.error_sample_count` MUST remain the total candidate count, not the visible list length

#### Scenario: Visible error sample count remains replay-only

- **WHEN** a caller inspects `runtime.probe_summary.error_sample_visible_count`
- **THEN** this field MUST NOT start sockets, mutate providers, schedule retry/backoff, request additional probes, or manage daemon lifecycle
- **AND** this field MUST NOT be treated as provider readiness, endpoint coverage, or live TongDaXin runtime health proof
