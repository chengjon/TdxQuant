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

#### Scenario: Caller requests a config-check summary view

- **WHEN** a caller executes `provider-replay config-check --config <path> --view summary`
- **THEN** the CLI MUST include a machine-readable `summary_view` derived from the loaded config
- **AND** the summary MUST indicate that the command did not start serving, did not request probes, and does not provide daemon lifecycle management
- **AND** the command MUST NOT expose bearer token values

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

### Requirement: Provider replay status CLI SHALL expose an opt-in summary view

The provider replay status CLI SHALL expose an opt-in summary view that projects existing lifecycle and probe-rollup fields without changing the default detailed status output or daemon lifecycle semantics.

#### Scenario: Caller requests provider replay status summary view

- **WHEN** a caller runs `provider-replay status --config <path> --view summary`
- **THEN** the command MUST include `summary_view`
- **AND** the summary view MUST include lifecycle boundary fields, runtime observation flags, `probe_summary`, compact read-only capability fields, and boundaries
- **AND** the summary view MUST NOT replace the detailed `status` payload
- **AND** the command MUST NOT start, stop, restart, supervise, or schedule a replay service

#### Scenario: Caller omits provider replay status summary view

- **WHEN** a caller runs `provider-replay status --config <path>` without `--view summary`
- **THEN** the command MUST keep returning the detailed status payload without `summary_view`

### Requirement: Provider replay status summary SHALL expose compact replay source

The provider replay status summary view SHALL expose compact replay-source provenance derived from the detailed status payload without copying full fixture path detail or changing daemon lifecycle semantics.

#### Scenario: Caller requests provider replay status summary source view

- **WHEN** a caller executes `provider-replay status --config <path> --view summary`
- **THEN** the summary view MUST include `replay_source.source_kind`
- **AND** the summary view MUST include `replay_source.fixture`
- **AND** the summary view MUST include `replay_source.fixture_path_provided`
- **AND** the summary view MUST NOT include full `replay_source.fixture_path`
- **AND** the command MUST NOT start, stop, restart, or supervise the replay service

### Requirement: Provider replay status summary SHALL expose compact security boundary

The provider replay status summary view SHALL expose compact security boundary metadata derived from the detailed status payload without exposing bearer tokens, allowlist members, or changing daemon lifecycle semantics.

#### Scenario: Caller requests provider replay status summary security view

- **WHEN** a caller executes `provider-replay status --config <path> --view summary`
- **THEN** the summary view MUST include `security.bearer_token_required`
- **AND** the summary view MUST include `security.source_allowlist_enabled`
- **AND** the summary view MUST include `security.master_allowlist_count`
- **AND** the summary view MUST NOT include bearer token values
- **AND** the summary view MUST NOT include full allowlist members
- **AND** the command MUST NOT start, stop, restart, or supervise the replay service

### Requirement: Provider replay status summary SHALL expose lifecycle support boundary

The provider replay status summary view SHALL expose compact lifecycle support metadata derived from the detailed lifecycle payload without adding start, stop, restart, scheduler, daemon, supervisor, live-session, or write behavior.

#### Scenario: Caller requests provider replay status lifecycle support summary

- **WHEN** a caller executes `provider-replay status --config <path> --view summary`
- **THEN** the summary view MUST include `lifecycle.control_supported`
- **AND** the summary view MUST include `lifecycle.managed_operation_count`
- **AND** `lifecycle.control_supported` MUST be `false` for the current replay provider
- **AND** `lifecycle.managed_operation_count` MUST be `0` for the current replay provider
- **AND** the command MUST NOT start, stop, restart, schedule, daemonize, supervise, or observe a live market session

### Requirement: Provider replay status summary SHALL expose bounded endpoint samples

The provider replay status summary view SHALL include bounded read-only endpoint samples derived from the detailed `capabilities.endpoints` list without exposing the complete endpoint list or changing replay service lifecycle/probe behavior.

#### Scenario: Caller requests provider replay status summary endpoint samples

- **WHEN** a caller runs `provider-replay status --config <path> --view summary`
- **THEN** `summary_view.capabilities` MUST include `endpoint_samples`
- **AND** `summary_view.capabilities` MUST include `endpoint_sample_limit`
- **AND** `summary_view.capabilities` MUST include `endpoint_sample_truncated`
- **AND** `summary_view.capabilities` MUST continue to include `endpoint_count`
- **AND** `summary_view.capabilities` MUST NOT include the full `endpoints` list
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, or probe unless explicit probe flags are provided

### Requirement: Provider replay status summary SHALL expose endpoint family counts

The provider replay status summary view SHALL include compact endpoint family counts derived from the detailed `capabilities.endpoints` list without exposing the complete endpoint list or changing replay service lifecycle/probe behavior.

#### Scenario: Caller requests provider replay status summary endpoint family counts

- **WHEN** a caller runs `provider-replay status --config <path> --view summary`
- **THEN** `summary_view.capabilities` MUST include `endpoint_family_counts`
- **AND** the counts MUST be derived from detailed `capabilities.endpoints`
- **AND** the counts MUST include replay `core` and `watch` families when matching endpoints exist
- **AND** `summary_view.capabilities` MUST NOT include the full `endpoints` list
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, or probe unless explicit probe flags are provided

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

