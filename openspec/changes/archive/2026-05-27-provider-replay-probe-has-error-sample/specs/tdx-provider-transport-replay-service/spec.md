## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose error-sample presence

Provider replay status SHALL include additive read-only `runtime.probe_summary.has_error_sample` derived only from existing normalized probe summary metadata.

#### Scenario: No error samples report false

- **WHEN** provider replay status is built without probe error samples
- **THEN** `runtime.probe_summary.has_error_sample` MUST be `false`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Error samples report true

- **WHEN** provider replay status contains one or more probe error samples
- **THEN** `runtime.probe_summary.has_error_sample` MUST be `true`
- **AND** the field MUST remain consistent with `error_sample_count > 0`

#### Scenario: Error-sample presence remains advisory

- **WHEN** provider replay status exposes `runtime.probe_summary.has_error_sample`
- **THEN** the field MUST NOT indicate that an additional probe, provider mutation, socket start, daemon lifecycle action, restart/backoff, scheduler action, or write behavior was executed
- **AND** the field MUST NOT claim broker readiness, provider readiness, endpoint coverage, or production daemon control
