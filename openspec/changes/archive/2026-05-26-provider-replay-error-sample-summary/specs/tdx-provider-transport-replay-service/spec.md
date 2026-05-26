## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose error sample summary

Provider replay status probe summaries SHALL include additive read-only `runtime.probe_summary.error_sample_summary` metadata derived from existing bounded error sample diagnostics without exposing full probe payloads, adding probe endpoints, mutating provider state, or managing daemon lifecycle.

#### Scenario: Status probe summary includes compact error sample metadata

- **WHEN** provider replay status probes produce one or more failed probe samples
- **THEN** `runtime.probe_summary.error_sample_summary.count` MUST equal the full error sample count
- **AND** `visible_count`, `hidden_count`, `limit`, and `truncated` MUST match the existing `error_sample_visible_count`, `error_sample_hidden_count`, `error_sample_limit`, and `error_sample_truncated` sibling fields
- **AND** `primary_probe`, `primary_status`, `primary_error_code`, `primary_http_status`, and `primary_reachability` MUST match the existing primary error sample sibling fields
- **AND** hidden counts MUST be non-negative integers
- **AND** the summary MUST NOT expose full probe payloads
- **AND** the summary MUST NOT add probe endpoints, start sockets, mutate provider state, or manage daemon lifecycle

#### Scenario: Status probe summary handles no failed probe samples

- **WHEN** provider replay status probes produce no failed probe samples
- **THEN** `runtime.probe_summary.error_sample_summary.count` MUST be `0`
- **AND** `visible_count` and `hidden_count` MUST be `0`
- **AND** `truncated` MUST be `false`
- **AND** primary fields MUST be `null`
- **AND** the summary MUST remain read-only and MUST NOT be treated as health/readiness proof
