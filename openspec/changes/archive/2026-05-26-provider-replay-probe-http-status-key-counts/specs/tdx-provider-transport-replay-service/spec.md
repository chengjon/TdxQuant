## ADDED Requirements

### Requirement: Provider Replay Probe HTTP Status Key Counts

Provider replay status SHALL expose read-only `runtime.probe_summary` HTTP status key-count fields derived from existing probe HTTP status count maps without requesting additional probes, changing health classification, starting sockets, mutating providers, or managing daemon lifecycle.

#### Scenario: Probe summary includes requested HTTP status key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `requested_http_status_counts`
- **THEN** `runtime.probe_summary.requested_http_status_key_count` MUST equal the number of keys in `requested_http_status_counts`
- **AND** this field MUST count distinct projected requested HTTP status keys, not probes or endpoints.

#### Scenario: Probe summary includes healthy HTTP status key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `healthy_http_status_counts`
- **THEN** `runtime.probe_summary.healthy_http_status_key_count` MUST equal the number of keys in `healthy_http_status_counts`
- **AND** this field MUST NOT imply service health, readiness, or endpoint coverage.

#### Scenario: Probe summary includes failed HTTP status key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `failed_http_status_counts`
- **THEN** `runtime.probe_summary.failed_http_status_key_count` MUST equal the number of keys in `failed_http_status_counts`
- **AND** this field MUST NOT imply live provider availability, daemon lifecycle control, or failure coverage completeness.
