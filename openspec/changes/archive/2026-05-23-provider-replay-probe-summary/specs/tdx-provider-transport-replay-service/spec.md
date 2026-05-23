## ADDED Requirements

### Requirement: Provider replay status SHALL summarize requested probe results

Provider replay status SHALL expose a `runtime.probe_summary` rollup derived from
the existing normalized probe objects without replacing those objects or changing
daemon lifecycle semantics.

#### Scenario: Caller builds status without requesting probes

- **WHEN** a caller builds provider replay status without supplying probe results
- **THEN** `runtime.probe_summary.status` MUST be `not_requested`
- **AND** `runtime.probe_summary.requested_count` MUST be `0`
- **AND** `runtime.probe_summary.not_requested_count` MUST include all supported status probes
- **AND** the individual probe objects MUST remain present with `status=not_requested`

#### Scenario: Caller includes healthy requested probes

- **WHEN** a caller builds provider replay status with one or more healthy probe results
- **THEN** `runtime.probe_summary.status` MUST be `healthy`
- **AND** `runtime.probe_summary.requested_count` MUST equal the number of requested probes
- **AND** `runtime.probe_summary.healthy_count` MUST equal the number of requested probes
- **AND** the summary MUST list the requested probe keys

#### Scenario: Caller includes a degraded requested probe

- **WHEN** a caller builds provider replay status with any requested probe whose status is not `healthy`
- **THEN** `runtime.probe_summary.status` MUST be `degraded`
- **AND** `runtime.probe_summary.failed_count` MUST be at least `1`
- **AND** the summary MUST list the unhealthy probe key
- **AND** the status MUST still state that daemon lifecycle management is not provided
