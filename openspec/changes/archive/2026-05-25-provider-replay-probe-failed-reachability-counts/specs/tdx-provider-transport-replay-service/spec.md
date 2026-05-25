## ADDED Requirements

### Requirement: Provider replay status SHALL summarize failed probe reachability

Provider replay status SHALL include additive `runtime.probe_summary.failed_reachability_counts` derived from existing requested non-healthy probe results without starting sockets, requesting additional probes, mutating provider state, or managing daemon lifecycle.

#### Scenario: No failed probes

- **WHEN** provider replay status is built without requested non-healthy probes
- **THEN** `runtime.probe_summary.failed_reachability_counts` MUST be an empty object
- **AND** no probe endpoint MUST be requested by this derived field

#### Scenario: Failed unreachable probes exist

- **WHEN** provider replay status is built with requested non-healthy probes whose `reachable` value is `false`
- **THEN** `runtime.probe_summary.failed_reachability_counts` MUST count those probes under `unreachable`
- **AND** the field MUST NOT include `healthy` or `not_requested` probes

#### Scenario: Failed reachability can be unknown

- **WHEN** provider replay status is built with requested non-healthy probes that omit a boolean `reachable` value
- **THEN** `runtime.probe_summary.failed_reachability_counts` MUST count those probes under `unknown`
- **AND** the field MUST remain a summary over existing probe objects only

#### Scenario: CLI summary preserves failed reachability counts

- **WHEN** a caller runs `provider-replay status --view summary`
- **THEN** the summary payload MUST include `probe_summary.failed_reachability_counts`
- **AND** the summary payload MUST remain a read-only projection
