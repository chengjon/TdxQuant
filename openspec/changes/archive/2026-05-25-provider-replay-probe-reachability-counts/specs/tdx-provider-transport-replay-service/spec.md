## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose requested reachability counts

Provider replay status SHALL include additive `runtime.probe_summary.requested_reachability_counts`, a compact count map derived only from requested fixed probe targets' normalized `reachable` values, without changing probe execution, replay lifecycle, daemon management, or write behavior.

#### Scenario: No requested probes have empty reachability counts

- **WHEN** provider replay status is built without requested probes
- **THEN** `runtime.probe_summary.requested_reachability_counts` MUST be an empty object
- **AND** no probe operation MUST be executed

#### Scenario: Requested probes are counted by reachability

- **WHEN** provider replay status includes requested probes
- **THEN** `runtime.probe_summary.requested_reachability_counts` MUST count `reachable=True` as `reachable`
- **AND** it MUST count `reachable=False` as `unreachable`
- **AND** it MUST count missing or non-boolean reachability as `unknown`
- **AND** `not_requested` probes MUST be excluded

#### Scenario: Summary view preserves requested reachability counts

- **WHEN** a caller requests `provider-replay status --view summary`
- **AND** the detailed status includes `runtime.probe_summary.requested_reachability_counts`
- **THEN** `summary_view.probe_summary.requested_reachability_counts` MUST mirror the detailed status probe summary
- **AND** the summary view MUST remain an opt-in compact projection, not a daemon-control API
