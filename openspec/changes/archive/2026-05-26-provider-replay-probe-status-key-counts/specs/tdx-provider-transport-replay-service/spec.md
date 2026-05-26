## ADDED Requirements

### Requirement: Provider Replay Probe Status Key Counts

Provider replay status SHALL expose read-only `runtime.probe_summary` status key-count fields derived from existing probe status count maps without requesting additional probes, changing health classification, starting sockets, mutating providers, or managing daemon lifecycle.

#### Scenario: Probe summary includes status key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `status_counts`
- **THEN** `runtime.probe_summary.status_key_count` MUST equal the number of keys in `status_counts`
- **AND** this field MUST count distinct projected probe status keys, not probes or endpoints.

#### Scenario: Probe summary includes requested status key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `requested_status_counts`
- **THEN** `runtime.probe_summary.requested_status_key_count` MUST equal the number of keys in `requested_status_counts`
- **AND** this field MUST NOT request probes or imply request coverage.

#### Scenario: Probe summary includes failed status key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `failed_status_counts`
- **THEN** `runtime.probe_summary.failed_status_key_count` MUST equal the number of keys in `failed_status_counts`
- **AND** this field MUST NOT imply service readiness, live provider availability, or daemon lifecycle control.
