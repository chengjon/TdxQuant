# tdx-provider-transport-replay-service Specification

## Purpose
TBD - created by archiving change provider-transport-replay-fixtures. Update Purpose after archive.
## Requirements
### Requirement: Provider transport replay service SHALL expose a fixture-backed HTTP surface
The system SHALL provide a small HTTP replay service that serves supported provider replay fixtures without live Windows runtime access.

#### Scenario: Replay service health reports replay-only mode
- **WHEN** a caller requests the replay service health endpoint with valid authorization
- **THEN** the service MUST return a successful machine-readable envelope
- **AND** the response MUST identify `provider_mode` as `replay`
- **AND** the response MUST NOT require TongDaXin runtime initialization

#### Scenario: Replay service exposes the built-in fixture catalog
- **WHEN** a caller requests the replay service fixture catalog
- **THEN** the service MUST return the same built-in fixture descriptors exposed by the replay fixture catalog helper
- **AND** each descriptor MUST preserve fixture name, capability, format, and relative path metadata

#### Scenario: Replay service serves a synchronous replay result
- **WHEN** a caller requests a supported synchronous capability through the replay service
- **THEN** the service MUST resolve the same default or explicit replay fixture as in-process replay mode
- **AND** the returned payload MUST preserve the provider result contract
- **AND** no live fallback MAY be attempted

### Requirement: Provider transport replay service SHALL simulate subscription-watch daemon read paths
The system SHALL expose read-only subscription-watch status, events, and event-stream endpoints backed by replay fixtures.

#### Scenario: Fake provider returns replay watch status
- **WHEN** a caller requests subscription-watch status from the replay service
- **THEN** the service MUST return replay fixture status projected as a daemon-backed watch status response
- **AND** the response MUST identify the source as replay fixture data

#### Scenario: Fake provider returns replay watch event rows
- **WHEN** a caller requests subscription-watch events from the replay service
- **THEN** the service MUST return replay fixture event rows in canonical subscription event shape
- **AND** the response MUST support a tail limit without changing the fixture source

#### Scenario: Fake provider streams replay watch frames
- **WHEN** a caller requests the subscription-watch replay event stream
- **THEN** the service MUST return Server-Sent Events frames with JSON `data` payloads
- **AND** the frames MUST include status, quote, heartbeat or terminal projections as appropriate for the fixture

### Requirement: Provider transport replay service SHALL support deterministic delayed playback metadata
The system SHALL allow replay stream callers to request delayed playback semantics without relying on live sleeps or nondeterministic timing.

#### Scenario: Delayed playback frames carry planned timing metadata
- **WHEN** a caller requests replay stream frames with delayed playback enabled
- **THEN** each emitted stream frame MUST include replay playback metadata
- **AND** quote frames MUST expose deterministic planned emit offsets derived from fixture order and requested delay

#### Scenario: Immediate playback remains the default
- **WHEN** a caller requests replay stream frames without delayed playback options
- **THEN** the service MUST emit frames in fixture order
- **AND** frame payloads MUST identify playback mode as `immediate`

### Requirement: Provider transport replay service SHALL enforce daemon-style access boundaries
The system SHALL protect the replay HTTP surface with the same minimal daemon access boundaries used by the bridge control plane.

#### Scenario: Replay service rejects missing or invalid bearer token
- **WHEN** a caller requests any replay HTTP endpoint without the configured bearer token
- **THEN** the service MUST reject the request with a machine-readable unauthorized error

#### Scenario: Replay service rejects disallowed source IP
- **WHEN** a caller requests any replay HTTP endpoint from a source outside the configured allowlist
- **THEN** the service MUST reject the request with a machine-readable forbidden-source error

### Requirement: Provider transport replay service SHALL expose foreground CLI startup

The system SHALL provide a CLI entry that loads a replay transport config and delegates to the existing foreground provider replay HTTP server.

#### Scenario: Caller validates a replay service config without opening a socket

- **WHEN** a caller executes `provider-replay config-check --config <path>`
- **THEN** the CLI MUST load the replay transport config and return a machine-readable summary
- **AND** the command MUST NOT start the HTTP server

#### Scenario: Caller starts the replay service in the foreground

- **WHEN** a caller executes `provider-replay serve --config <path>`
- **THEN** the CLI MUST load the replay transport config and call the existing foreground server runner
- **AND** the command MUST NOT imply daemon start/stop lifecycle management

### Requirement: Provider transport replay service SHALL expose lifecycle boundary status

The system SHALL provide a replay fake-provider status summary that distinguishes configured replay capabilities from managed daemon lifecycle support.

#### Scenario: Caller inspects replay fake-provider status without starting a server

- **WHEN** a caller builds replay fake-provider status from a valid provider transport replay config
- **THEN** the status MUST identify the provider, bind address, configured replay source, and replay-only transport mode
- **AND** it MUST list the read-only HTTP endpoints covered by the fake-provider surface
- **AND** it MUST state that runtime state is not observed by this summary
- **AND** it MUST state that daemon start/stop lifecycle management is not provided

#### Scenario: Caller requests replay fake-provider status through the CLI

- **WHEN** a caller executes `provider-replay status --config <path>`
- **THEN** the CLI MUST load the replay transport config and return the lifecycle boundary status
- **AND** the command MUST NOT open a socket or start the foreground server
- **AND** the command MUST NOT imply live market session support

### Requirement: Provider replay status SHALL optionally probe configured replay service health

The provider replay lifecycle status SHALL support an explicit, read-only health probe for the configured replay HTTP service without taking ownership of daemon lifecycle management.

#### Scenario: Caller builds status without requesting a health probe

- **WHEN** a caller builds provider replay lifecycle status without a probe result
- **THEN** the status MUST remain static and report `runtime.health_probe.status=not_requested`
- **AND** it MUST continue to report `runtime.runtime_observed=false`

#### Scenario: Caller requests a provider replay health probe

- **WHEN** a caller explicitly requests a provider replay health probe for a configured replay service
- **THEN** the probe MUST call the configured `/provider/v1/replay/health` endpoint with the configured bearer token
- **AND** the resulting status MUST report whether the replay service was reachable, the HTTP status if available, and the configured timeout
- **AND** the status MUST NOT expose the bearer token
- **AND** lifecycle fields MUST continue to report no managed start/stop/restart behavior

#### Scenario: Caller requests provider-replay status probe through the CLI

- **WHEN** a caller executes `provider-replay status --config <path> --probe-health`
- **THEN** the CLI MUST include the explicit replay health probe result in the returned lifecycle status
- **AND** the command MUST NOT start, stop, restart, or supervise the replay service

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

### Requirement: Provider replay status SHALL support an all-surfaces probe shortcut
The provider replay status CLI SHALL expose a `--probe-all` shortcut that enables all existing read-only status probes without changing lifecycle management behavior.

#### Scenario: Caller probes all provider replay surfaces
- **WHEN** a caller runs `provider-replay status --probe-all`
- **THEN** the status command MUST request health, watch-status, watch-events, and watch-stream probes
- **AND** each probe MUST use the configured token and probe timeout
- **AND** lifecycle `start_stop_managed=false` and `daemon_managed=false` MUST remain unchanged

#### Scenario: Caller uses individual probe flags
- **WHEN** a caller runs `provider-replay status` with any existing individual probe flag
- **THEN** that individual probe behavior MUST remain available
- **AND** `--probe-all` MUST NOT be required for narrow checks

