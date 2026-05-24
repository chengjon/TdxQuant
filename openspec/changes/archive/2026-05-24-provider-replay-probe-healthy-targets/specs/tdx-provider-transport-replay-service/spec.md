# tdx-provider-transport-replay-service Delta

## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose healthy probe targets

Provider replay status SHALL include an additive `runtime.probe_summary.healthy` list derived from existing probe result statuses without starting sockets, managing daemon lifecycle, scheduling restarts, or enabling write behavior.

#### Scenario: No requested probes have empty healthy target list

- **WHEN** provider replay status is built without requested probes
- **THEN** `runtime.probe_summary.status` MUST be `not_requested`
- **AND** `runtime.probe_summary.healthy` MUST be an empty list
- **AND** the status call MUST remain read-only

#### Scenario: Healthy requested probes are listed

- **WHEN** provider replay status includes requested probes whose status is `healthy`
- **THEN** `runtime.probe_summary.healthy` MUST list those probe targets
- **AND** the list order MUST follow the provider replay probe target order
- **AND** existing count fields and `runtime.probe_summary.unhealthy` MUST remain derived from the same probe objects

#### Scenario: Summary view carries probe summary healthy targets

- **WHEN** `provider-replay status --view summary` is requested
- **THEN** the `summary_view.probe_summary.healthy` list MUST match `status.runtime.probe_summary.healthy`
- **AND** the summary view MUST remain an opt-in compact projection, not a daemon-control API
