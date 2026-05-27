## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose hidden error-sample presence

Provider replay status SHALL include additive read-only `runtime.probe_summary.has_hidden_error_sample` derived only from existing normalized probe summary metadata.

#### Scenario: No hidden error samples report false

- **WHEN** provider replay status has no error samples hidden by the sample limit
- **THEN** `runtime.probe_summary.has_hidden_error_sample` MUST be `false`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Hidden error samples report true

- **WHEN** provider replay status has one or more error samples hidden by the sample limit
- **THEN** `runtime.probe_summary.has_hidden_error_sample` MUST be `true`
- **AND** the field MUST remain consistent with `error_sample_hidden_count > 0`

#### Scenario: Hidden error-sample presence remains advisory

- **WHEN** provider replay status exposes `runtime.probe_summary.has_hidden_error_sample`
- **THEN** the field MUST NOT indicate that an additional probe, provider mutation, socket start, daemon lifecycle action, restart/backoff, scheduler action, or write behavior was executed
- **AND** the field MUST NOT claim broker readiness, provider readiness, endpoint coverage, or production daemon control
