## ADDED Requirements

### Requirement: Provider replay status SHALL optionally probe watch event-stream surface reachability
The system SHALL allow provider replay lifecycle status to optionally probe the read-only watch event-stream endpoint of an already-running replay service without starting, stopping, restarting, daemonizing, scheduling, or supervising that service.

#### Scenario: Caller probes watch event-stream endpoint from provider-replay status
- **WHEN** a caller runs `provider-replay status --probe-watch-stream`
- **THEN** the status output MUST include `runtime.watch_stream_probe`
- **AND** the probe MUST target `/provider/v1/replay/watch/events/stream` using the configured token and timeout
- **AND** the status MUST keep lifecycle `start_stop_managed=false` and `daemon_managed=false`

#### Scenario: Caller omits watch event-stream probe
- **WHEN** a caller runs `provider-replay status` without `--probe-watch-stream`
- **THEN** the status output MUST keep `runtime.watch_stream_probe.status=not_requested`
- **AND** no watch event-stream HTTP request MUST be required
