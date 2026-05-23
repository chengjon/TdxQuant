## ADDED Requirements

### Requirement: Provider replay status SHALL optionally probe watch-status surface reachability
The system SHALL allow provider replay lifecycle status to optionally probe the read-only watch-status endpoint of an already-running replay service without starting, stopping, restarting, or daemonizing that service.

#### Scenario: Caller probes watch-status endpoint from provider-replay status
- **WHEN** a caller runs `provider-replay status --probe-watch-status`
- **THEN** the status output MUST include `runtime.watch_status_probe`
- **AND** the probe MUST target `/provider/v1/replay/watch/status` using the configured token and timeout
- **AND** the status MUST keep lifecycle `start_stop_managed=false` and `daemon_managed=false`

#### Scenario: Caller omits watch-status probe
- **WHEN** a caller runs `provider-replay status` without `--probe-watch-status`
- **THEN** the status output MUST keep `runtime.watch_status_probe.status=not_requested`
- **AND** no watch-status HTTP request MUST be required
