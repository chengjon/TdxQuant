# tdx-provider-transport-replay-service Delta

## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose requested status counts

Provider replay status SHALL include additive `runtime.probe_summary.requested_status_counts`, a compact count map derived only from requested fixed probe targets without changing probe execution, replay lifecycle, daemon management, or write behavior.

#### Scenario: No requested probes have empty requested status counts

- **WHEN** provider replay status is built without requested probes
- **THEN** `runtime.probe_summary.status` MUST be `not_requested`
- **AND** `runtime.probe_summary.requested_status_counts` MUST be an empty object
- **AND** no probe operation MUST be executed

#### Scenario: Healthy requested probes are counted

- **WHEN** provider replay status includes a requested probe whose status is `healthy`
- **THEN** `runtime.probe_summary.requested_status_counts` MUST count `healthy`
- **AND** `runtime.probe_summary.status_counts` MUST continue counting not-requested probes as well

#### Scenario: Degraded requested probes are counted

- **WHEN** provider replay status includes a requested probe whose status is not `healthy`
- **THEN** `runtime.probe_summary.requested_status_counts` MUST count the requested probe status
- **AND** the replay service MUST NOT start, stop, restart, daemonize, schedule, or supervise as part of status construction

