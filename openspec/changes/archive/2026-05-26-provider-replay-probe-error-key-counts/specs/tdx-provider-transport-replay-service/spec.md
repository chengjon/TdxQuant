## ADDED Requirements

### Requirement: Provider Replay Probe Error Key Counts

Provider replay status SHALL expose read-only `runtime.probe_summary` error key-count fields derived from existing error-code and error-sample count maps without requesting additional probes, exposing full probe payloads, starting sockets, mutating providers, or managing daemon lifecycle.

#### Scenario: Probe summary includes error-code key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `error_code_counts`
- **THEN** `runtime.probe_summary.error_code_key_count` MUST equal the number of keys in `error_code_counts`
- **AND** this field MUST count distinct projected error-code keys, not probes or full error payloads.

#### Scenario: Probe summary includes failed error-code key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `failed_error_code_counts`
- **THEN** `runtime.probe_summary.failed_error_code_key_count` MUST equal the number of keys in `failed_error_code_counts`
- **AND** this field MUST NOT imply failure coverage completeness.

#### Scenario: Probe summary includes error-sample status key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `error_sample_status_counts`
- **THEN** `runtime.probe_summary.error_sample_status_key_count` MUST equal the number of keys in `error_sample_status_counts`
- **AND** this field MUST NOT expose full sample payloads.

#### Scenario: Probe summary includes error-sample probe key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `error_sample_probe_counts`
- **THEN** `runtime.probe_summary.error_sample_probe_key_count` MUST equal the number of keys in `error_sample_probe_counts`
- **AND** this field MUST NOT imply health, readiness, live provider availability, or daemon lifecycle control.
