## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose error sample reachability counts

Provider replay status output SHALL include additive read-only `runtime.probe_summary.error_sample_reachability_counts` and `runtime.probe_summary.error_sample_reachability_key_count` fields derived from existing error sample candidate probes' normalized reachability buckets, without changing probe execution, replay lifecycle, daemon management, scheduler, restart/backoff, configured endpoints, or provider mutation behavior.

#### Scenario: No error sample reachability candidates

- **WHEN** provider replay status is built without requested error sample candidates
- **THEN** `runtime.probe_summary.error_sample_reachability_counts` MUST be an empty object
- **AND** `runtime.probe_summary.error_sample_reachability_key_count` MUST be `0`
- **AND** existing `error_sample_count`, `error_sample_status_counts`, `error_sample_probe_counts`, `error_samples`, and `error_sample_truncated` fields MUST remain available

#### Scenario: Error sample candidates include reachability states

- **WHEN** provider replay status has error sample candidates with boolean or missing reachability values
- **THEN** `runtime.probe_summary.error_sample_reachability_counts` MUST count `reachable=True` as `reachable`
- **AND** it MUST count `reachable=False` as `unreachable`
- **AND** it MUST count missing or non-boolean reachability as `unknown`
- **AND** `runtime.probe_summary.error_sample_reachability_key_count` MUST equal the number of distinct reachability keys
- **AND** the count map MUST be independent of the bounded `error_samples` list truncation
- **AND** existing probe execution, replay lifecycle, daemon management, scheduler, restart/backoff, configured endpoints, and provider mutation behavior MUST remain unchanged

#### Scenario: Summary view includes error sample reachability counts

- **WHEN** a caller runs `provider-replay status --view summary` and the underlying probe summary includes `error_sample_reachability_counts`
- **THEN** `summary_view.probe_summary.error_sample_reachability_counts` MUST mirror the detailed runtime probe summary
- **AND** `summary_view.probe_summary.error_sample_reachability_key_count` MUST mirror the detailed runtime probe summary
- **AND** the summary view MUST NOT expose secrets, full probe payloads, daemon lifecycle controls, or provider mutation behavior
