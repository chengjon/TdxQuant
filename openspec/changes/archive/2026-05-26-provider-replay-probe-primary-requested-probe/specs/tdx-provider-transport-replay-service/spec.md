## ADDED Requirements

### Requirement: Provider Replay Primary Requested Probe Summary

Provider replay status SHALL expose a read-only `runtime.probe_summary.primary_requested_probe` field derived from the existing requested probe target list, without requesting additional probes, changing health classification, starting sockets, mutating providers, or managing daemon lifecycle.

#### Scenario: No probe requested

- **GIVEN** provider replay status is requested without any `--probe-*` option
- **WHEN** the probe summary is built
- **THEN** `runtime.probe_summary.primary_requested_probe` MUST be `null`
- **AND** this MUST NOT request or execute any probe.

#### Scenario: Requested probes present

- **GIVEN** provider replay status is requested with one or more explicit probe targets
- **WHEN** the probe summary is built
- **THEN** `runtime.probe_summary.primary_requested_probe` MUST equal the first item in `runtime.probe_summary.requested`
- **AND** this field MUST NOT imply health, readiness, endpoint coverage, or lifecycle control.

#### Scenario: CLI summary includes primary requested probe

- **GIVEN** provider replay status is requested with `--view summary` and one or more explicit probe targets
- **WHEN** the CLI summary view is emitted
- **THEN** `probe_summary.primary_requested_probe` MUST equal the first item in `probe_summary.requested`
- **AND** this field MUST remain a compact read-only diagnostic hint.
