# tdx-provider-transport-replay-service Delta

## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose status counts

The provider replay status payload SHALL include `runtime.probe_summary.status_counts`, a compact count map derived from the fixed replay probe statuses without changing probe execution, replay lifecycle, or daemon management behavior.

#### Scenario: Caller requests replay status without probes

- **WHEN** a caller builds provider replay status without enabling any probes
- **THEN** `runtime.probe_summary.status_counts` MUST count all fixed probes as `not_requested`
- **AND** no probe operation MUST be executed

#### Scenario: Caller requests replay status with successful probes

- **WHEN** a caller builds provider replay status with successful enabled probes
- **THEN** `runtime.probe_summary.status_counts` MUST count healthy probes as `healthy`
- **AND** the existing requested, healthy, failed, and not-requested count fields MUST remain present
- **AND** the replay service MUST NOT start, stop, restart, daemonize, schedule, or supervise as part of status construction
