## ADDED Requirements

### Requirement: Provider Replay Probe Reachability Key Counts

Provider replay status SHALL expose read-only `runtime.probe_summary` reachability key-count fields derived from existing probe reachability count maps without requesting additional probes, changing health classification, starting sockets, mutating providers, or managing daemon lifecycle.

#### Scenario: Probe summary includes requested reachability key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `requested_reachability_counts`
- **THEN** `runtime.probe_summary.requested_reachability_key_count` MUST equal the number of keys in `requested_reachability_counts`
- **AND** this field MUST count distinct projected requested reachability keys, not probes or endpoints.

#### Scenario: Probe summary includes healthy reachability key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `healthy_reachability_counts`
- **THEN** `runtime.probe_summary.healthy_reachability_key_count` MUST equal the number of keys in `healthy_reachability_counts`
- **AND** this field MUST NOT imply service health, readiness, or endpoint coverage.

#### Scenario: Probe summary includes failed reachability key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `failed_reachability_counts`
- **THEN** `runtime.probe_summary.failed_reachability_key_count` MUST equal the number of keys in `failed_reachability_counts`
- **AND** this field MUST NOT imply live provider availability, daemon lifecycle control, or failure coverage completeness.
