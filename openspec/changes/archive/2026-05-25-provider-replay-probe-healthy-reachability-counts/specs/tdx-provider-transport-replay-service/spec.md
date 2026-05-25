## ADDED Requirements

### Requirement: Provider replay status SHALL summarize healthy probe reachability

Provider replay status SHALL include additive `runtime.probe_summary.healthy_reachability_counts` derived from existing requested healthy probe results without starting sockets, requesting additional probes, mutating provider state, or managing daemon lifecycle.

#### Scenario: No healthy probes

- **WHEN** provider replay status is built without requested healthy probes
- **THEN** `runtime.probe_summary.healthy_reachability_counts` MUST be an empty object
- **AND** no probe endpoint MUST be requested by this derived field

#### Scenario: Healthy reachable probes exist

- **WHEN** provider replay status is built with requested healthy probes whose `reachable` value is `true`
- **THEN** `runtime.probe_summary.healthy_reachability_counts` MUST count those probes under `reachable`
- **AND** the field MUST NOT include failed or `not_requested` probes

#### Scenario: Healthy reachability can be unknown

- **WHEN** provider replay status is built with requested healthy probes that omit a boolean `reachable` value
- **THEN** `runtime.probe_summary.healthy_reachability_counts` MUST count those probes under `unknown`
- **AND** the field MUST remain a summary over existing probe objects only

#### Scenario: CLI summary preserves healthy reachability counts

- **WHEN** a caller runs `provider-replay status --view summary`
- **THEN** the summary payload MUST include `probe_summary.healthy_reachability_counts`
- **AND** the summary payload MUST remain a read-only projection
