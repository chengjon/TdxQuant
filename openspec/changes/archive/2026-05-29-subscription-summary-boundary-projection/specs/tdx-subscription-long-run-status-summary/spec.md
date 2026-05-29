## ADDED Requirements

### Requirement: Subscription summary views SHALL expose status summary boundary

CLI and HTTP subscription-watch summary views SHALL preserve the existing `status_summary.boundary` field when detailed status summary includes it.

#### Scenario: CLI summary view includes status summary boundary

- **WHEN** `bridge watch-status --view summary` is requested
- **AND** detailed status includes `status_summary.boundary`
- **THEN** the CLI summary payload MUST include `status_summary.boundary`
- **AND** the boundary MUST be copied without changing lifecycle behavior

#### Scenario: HTTP summary view includes status summary boundary

- **WHEN** HTTP `GET /bridge/v1/watch/status?view=summary` is requested
- **AND** detailed status includes `status_summary.boundary`
- **THEN** the HTTP summary payload MUST include `status_summary.boundary`
- **AND** the boundary MUST be copied without changing lifecycle behavior

#### Scenario: Status summary boundary remains non-executing

- **WHEN** summary views preserve `status_summary.boundary`
- **THEN** the projection MUST NOT start, stop, restart, supervise, backoff, probe, mutate provider state, stream events, or claim provider/broker/trading readiness
