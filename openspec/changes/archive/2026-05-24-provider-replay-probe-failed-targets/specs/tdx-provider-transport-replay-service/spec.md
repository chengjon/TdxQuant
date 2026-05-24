## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose failed probe targets

Provider replay status SHALL include additive `runtime.probe_summary.failed` derived from existing fixed probe statuses without changing probe execution, socket startup, daemon lifecycle, restart/backoff, or write behavior.

#### Scenario: Not-requested probe summary has no failed targets

- **WHEN** provider replay status is built without requested probes
- **THEN** `runtime.probe_summary.failed` MUST be an empty list
- **AND** `runtime.probe_summary.failed_count` MUST be `0`

#### Scenario: Degraded probe summary lists failed targets

- **WHEN** provider replay status includes a failed or unhealthy requested probe
- **THEN** `runtime.probe_summary.failed` MUST list that fixed probe key
- **AND** `runtime.probe_summary.failed_count` MUST equal the number of failed targets

#### Scenario: Status summary view preserves failed targets

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** the summary view probe summary MUST include `failed`
- **AND** the summary view `failed` value MUST mirror the detailed status probe summary
