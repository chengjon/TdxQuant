## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose primary error sample reachability

Provider replay status output SHALL include additive read-only `runtime.probe_summary.primary_error_sample_reachability` derived from the first existing error sample candidate's normalized reachability bucket, without changing `error_samples` payload shape, probe execution, replay lifecycle, daemon management, scheduler, restart/backoff, configured endpoints, or provider mutation behavior.

#### Scenario: No primary error sample reachability exists

- **WHEN** provider replay status is built without error sample candidates
- **THEN** `runtime.probe_summary.primary_error_sample_reachability` MUST be `null`
- **AND** existing primary error sample probe/status/error-code/HTTP-status fields MUST remain `null`
- **AND** existing `error_samples`, `error_sample_count`, and error sample count maps MUST remain available

#### Scenario: First error sample candidate has reachability

- **WHEN** provider replay status has error sample candidates
- **THEN** `runtime.probe_summary.primary_error_sample_reachability` MUST describe the first candidate's reachability as `reachable`, `unreachable`, or `unknown`
- **AND** it MUST use the same first-candidate ordering as `primary_error_sample_probe`
- **AND** `error_samples` payload shape and ordering MUST remain unchanged
- **AND** existing probe execution, replay lifecycle, daemon management, scheduler, restart/backoff, configured endpoints, and provider mutation behavior MUST remain unchanged

#### Scenario: Summary view includes primary error sample reachability

- **WHEN** a caller runs `provider-replay status --view summary` and the underlying probe summary includes `primary_error_sample_reachability`
- **THEN** `summary_view.probe_summary.primary_error_sample_reachability` MUST mirror the detailed runtime probe summary
- **AND** the summary view MUST NOT expose secrets, full probe payloads, daemon lifecycle controls, or provider mutation behavior
