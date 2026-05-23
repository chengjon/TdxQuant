## ADDED Requirements

### Requirement: Provider replay status SHALL optionally probe watch-events surface reachability
The system SHALL allow provider replay lifecycle status to optionally probe the read-only watch-events endpoint of an already-running replay service without starting, stopping, restarting, daemonizing, or scheduling that service.

#### Scenario: Caller probes watch-events endpoint from provider-replay status
- **WHEN** a caller runs `provider-replay status --probe-watch-events`
- **THEN** the status output MUST include `runtime.watch_events_probe`
- **AND** the probe MUST target `/provider/v1/replay/watch/events` using the configured token and timeout
- **AND** the status MUST keep lifecycle `start_stop_managed=false` and `daemon_managed=false`

#### Scenario: Caller omits watch-events probe
- **WHEN** a caller runs `provider-replay status` without `--probe-watch-events`
- **THEN** the status output MUST keep `runtime.watch_events_probe.status=not_requested`
- **AND** no watch-events HTTP request MUST be required
