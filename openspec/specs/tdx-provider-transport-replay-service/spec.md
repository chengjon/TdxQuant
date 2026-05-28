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

### Requirement: Provider replay probe summary SHALL expose not-requested targets

Provider replay status SHALL include an additive `runtime.probe_summary.not_requested` list identifying probe targets whose normalized status is `not_requested`, without starting sockets, executing unrequested probes, or managing daemon lifecycle.

#### Scenario: No probes requested lists every target

- **WHEN** provider replay status is built without explicit probe results
- **THEN** `runtime.probe_summary.not_requested` MUST contain every supported probe target in stable order
- **AND** `runtime.probe_summary.requested_count` MUST remain `0`
- **AND** the status MUST remain read-only

#### Scenario: Partial probes list skipped targets

- **WHEN** provider replay status is built with only a subset of explicit probe results
- **THEN** `runtime.probe_summary.not_requested` MUST list only the targets that were not requested
- **AND** `runtime.probe_summary.requested` MUST list the requested targets
- **AND** probe status counts MUST remain derived from normalized probe statuses

#### Scenario: CLI summary preserves not-requested targets

- **WHEN** `provider-replay status --view summary` is requested
- **THEN** `summary_view.probe_summary.not_requested` MUST preserve the detailed probe summary list
- **AND** the summary view MUST remain a read-only projection

### Requirement: Provider replay status SHALL expose probe total count

Provider replay status SHALL include an additive read-only `runtime.probe_summary.total_count` scalar derived from the fixed supported probe key list without adding probe targets, requesting probes, starting sockets, or changing daemon lifecycle semantics.

#### Scenario: Detailed status includes total supported probe count

- **WHEN** a caller builds provider replay status
- **THEN** `runtime.probe_summary.total_count` MUST equal the number of supported provider replay status probes
- **AND** `runtime.probe_summary.requested_count + runtime.probe_summary.not_requested_count` MUST equal `runtime.probe_summary.total_count`
- **AND** the individual probe objects MUST remain present

#### Scenario: Summary view preserves total supported probe count

- **WHEN** a caller runs `provider-replay status --config <path> --view summary`
- **THEN** `summary_view.probe_summary.total_count` MUST match the detailed `runtime.probe_summary.total_count`
- **AND** the summary view MUST remain read-only projection data
- **AND** the command MUST NOT start, stop, restart, supervise, or schedule a replay service

### Requirement: Provider replay status SHALL expose unhealthy probe count

Provider replay status SHALL include an additive read-only `runtime.probe_summary.unhealthy_count` scalar derived from existing probe status rollup data without adding probe targets, requesting probes, starting sockets, or changing daemon lifecycle semantics.

#### Scenario: Detailed status includes unhealthy probe count

- **WHEN** a caller builds provider replay status
- **THEN** `runtime.probe_summary.unhealthy_count` MUST equal the number of entries in `runtime.probe_summary.unhealthy`
- **AND** `runtime.probe_summary.unhealthy_count` MUST equal `runtime.probe_summary.failed_count`
- **AND** the individual probe objects MUST remain present

#### Scenario: Summary view preserves unhealthy probe count

- **WHEN** a caller requests provider replay status with `--view summary`
- **THEN** `summary_view.probe_summary.unhealthy_count` MUST equal the detailed `runtime.probe_summary.unhealthy_count`
- **AND** the summary view MUST remain a read-only projection

### Requirement: Provider replay status SHALL summarize probe error codes

Provider replay status SHALL expose additive `runtime.probe_summary.error_code_counts` derived from existing normalized probe objects, without starting sockets, managing daemon lifecycle, changing probe endpoints, or exposing secrets.

#### Scenario: No requested probe errors produce empty counts

- **WHEN** a caller builds provider replay status without unhealthy probe error codes
- **THEN** `runtime.probe_summary.error_code_counts` MUST be an empty object
- **AND** existing probe status counts and target lists MUST remain unchanged

#### Scenario: Unhealthy probe errors are counted by code

- **WHEN** a caller builds provider replay status with one or more probe objects that include `error_code`
- **THEN** `runtime.probe_summary.error_code_counts` MUST count each error code
- **AND** the probe summary status MUST remain derived from requested and unhealthy probes
- **AND** the status operation MUST remain read-only and MUST NOT manage daemon lifecycle

#### Scenario: CLI summary view preserves probe error-code counts

- **WHEN** a caller runs `provider-replay status --view summary`
- **AND** the underlying runtime probe summary includes `error_code_counts`
- **THEN** `summary_view.probe_summary.error_code_counts` MUST mirror the detailed runtime probe summary
- **AND** the summary view MUST remain a read-only projection

### Requirement: Provider replay status SHALL expose bounded probe error samples

Provider replay status SHALL include additive `runtime.probe_summary.error_samples`, `error_sample_limit`, and `error_sample_truncated` fields derived from existing normalized probe objects, without starting sockets, managing daemon lifecycle, changing probe endpoints, or exposing secrets.

#### Scenario: No probe errors produce empty samples

- **WHEN** a caller builds provider replay status without unhealthy probe errors
- **THEN** `runtime.probe_summary.error_samples` MUST be an empty list
- **AND** `runtime.probe_summary.error_sample_limit` MUST identify the sample cap
- **AND** `runtime.probe_summary.error_sample_truncated` MUST be `false`

#### Scenario: Probe errors produce compact bounded samples

- **WHEN** a caller builds provider replay status with unhealthy or error-classified probe objects
- **THEN** `runtime.probe_summary.error_samples` MUST include compact probe metadata
- **AND** each sample MUST include the probe key and normalized status
- **AND** samples MAY include `error_code` and `http_status` when present
- **AND** the sample list MUST NOT expose secret tokens, allowlist members, or full raw probe payloads

#### Scenario: CLI summary view preserves probe error samples

- **WHEN** a caller runs `provider-replay status --view summary`
- **AND** the underlying runtime probe summary includes `error_samples`
- **THEN** `summary_view.probe_summary.error_samples` MUST mirror the detailed runtime probe summary
- **AND** the summary view MUST remain a read-only projection

### Requirement: Provider replay probe summary SHALL expose failed probe targets

Provider replay status SHALL include additive `runtime.probe_summary.failed` derived from existing fixed probe statuses without changing probe execution, socket startup, daemon lifecycle, restart/backoff, or write behavior.

#### Scenario: Not-requested probe summary has no failed targets

- **WHEN** provider replay status is built without requested probes
- **THEN** `runtime.probe_summary.failed` MUST be an empty list
- **AND** `runtime.probe_summary.failed_count` MUST be `0`

#### Scenario: Degraded probe summary lists failed targets

- **WHEN** provider replay status includes a failed or unhealthy requested probe
- **THEN** `runtime.probe_summary.failed` MUST list that fixed probe key
- **AND** `runtime.probe_summary.failed_count` MUST equal the number of failed targets

#### Scenario: Status summary view preserves failed targets

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** the summary view probe summary MUST include `failed`
- **AND** the summary view `failed` value MUST mirror the detailed status probe summary

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

### Requirement: Provider replay probe summary SHALL expose failed status counts

Provider replay status SHALL include additive `runtime.probe_summary.failed_status_counts`, a compact count map derived only from requested fixed probe targets whose normalized status is not `healthy`, without changing probe execution, replay lifecycle, daemon management, or write behavior.

#### Scenario: No requested failures have empty failed status counts

- **WHEN** provider replay status is built without requested failed probes
- **THEN** `runtime.probe_summary.failed_status_counts` MUST be an empty object
- **AND** existing requested, healthy, failed, unhealthy, and not-requested target lists MUST remain present

#### Scenario: Degraded requested probes are counted by failed status

- **WHEN** provider replay status includes a requested probe whose status is not `healthy`
- **THEN** `runtime.probe_summary.failed_status_counts` MUST count that requested probe status
- **AND** `runtime.probe_summary.requested_status_counts` MUST continue counting all requested probe statuses
- **AND** the status operation MUST remain read-only and MUST NOT manage daemon lifecycle

#### Scenario: Summary view preserves failed status counts

- **WHEN** a caller requests `provider-replay status --view summary`
- **AND** the detailed status includes `runtime.probe_summary.failed_status_counts`
- **THEN** `summary_view.probe_summary.failed_status_counts` MUST mirror the detailed status probe summary
- **AND** the summary view MUST remain an opt-in compact projection, not a daemon-control API

### Requirement: Provider replay probe summary SHALL expose requested reachability counts

Provider replay status SHALL include additive `runtime.probe_summary.requested_reachability_counts`, a compact count map derived only from requested fixed probe targets' normalized `reachable` values, without changing probe execution, replay lifecycle, daemon management, or write behavior.

#### Scenario: No requested probes have empty reachability counts

- **WHEN** provider replay status is built without requested probes
- **THEN** `runtime.probe_summary.requested_reachability_counts` MUST be an empty object
- **AND** no probe operation MUST be executed

#### Scenario: Requested probes are counted by reachability

- **WHEN** provider replay status includes requested probes
- **THEN** `runtime.probe_summary.requested_reachability_counts` MUST count `reachable=True` as `reachable`
- **AND** it MUST count `reachable=False` as `unreachable`
- **AND** it MUST count missing or non-boolean reachability as `unknown`
- **AND** `not_requested` probes MUST be excluded

#### Scenario: Summary view preserves requested reachability counts

- **WHEN** a caller requests `provider-replay status --view summary`
- **AND** the detailed status includes `runtime.probe_summary.requested_reachability_counts`
- **THEN** `summary_view.probe_summary.requested_reachability_counts` MUST mirror the detailed status probe summary
- **AND** the summary view MUST remain an opt-in compact projection, not a daemon-control API

### Requirement: Provider replay probe summary SHALL expose requested HTTP status counts

Provider replay status SHALL include additive `runtime.probe_summary.requested_http_status_counts`, a compact count map derived only from requested fixed probe targets' integer `http_status` values, without changing probe execution, replay lifecycle, daemon management, or write behavior.

#### Scenario: No requested HTTP statuses have empty counts

- **WHEN** provider replay status is built without requested probes that have integer HTTP status values
- **THEN** `runtime.probe_summary.requested_http_status_counts` MUST be an empty object
- **AND** no probe operation MUST be executed

#### Scenario: Requested probes are counted by HTTP status

- **WHEN** provider replay status includes requested probes with integer `http_status` values
- **THEN** `runtime.probe_summary.requested_http_status_counts` MUST count each observed HTTP status code
- **AND** map keys MUST be stringified HTTP status codes
- **AND** `not_requested` probes MUST be excluded

#### Scenario: Summary view preserves requested HTTP status counts

- **WHEN** a caller requests `provider-replay status --view summary`
- **AND** the detailed status includes `runtime.probe_summary.requested_http_status_counts`
- **THEN** `summary_view.probe_summary.requested_http_status_counts` MUST mirror the detailed status probe summary
- **AND** the summary view MUST remain an opt-in compact projection, not a daemon-control API

### Requirement: Provider replay probe summary SHALL expose failed error-code counts

The provider replay status result SHALL include an additive `runtime.probe_summary.failed_error_code_counts` object derived from requested non-healthy probe error codes without starting sockets, adding probe endpoints, or managing daemon lifecycle.

#### Scenario: No requested probes have empty failed error-code counts

- **WHEN** provider replay status is built without requested probes
- **THEN** `runtime.probe_summary.failed_error_code_counts` MUST be an empty object
- **AND** `runtime.probe_summary.not_requested_count` MUST remain unchanged

#### Scenario: Failed requested probes have failed error-code counts

- **WHEN** a requested probe is non-healthy and includes a string `error_code`
- **THEN** `runtime.probe_summary.failed_error_code_counts` MUST count that error code
- **AND** healthy and `not_requested` probes MUST NOT contribute to failed error-code counts
- **AND** the rollup MUST remain a read-only summary

#### Scenario: Summary view preserves failed error-code counts

- **WHEN** a caller requests provider replay status with `--view summary`
- **THEN** the summary view MUST include `probe_summary.failed_error_code_counts`
- **AND** the summary view MUST remain a read-only projection

### Requirement: Provider replay probe summary SHALL expose healthy HTTP status counts

Provider replay status output SHALL include additive `runtime.probe_summary.healthy_http_status_counts` derived from requested healthy probe HTTP statuses without changing probe execution, daemon lifecycle, scheduler, restart, or provider mutation behavior.

#### Scenario: No requested probes have no healthy HTTP status counts

- **WHEN** provider replay status is built without requested probes
- **THEN** `runtime.probe_summary.healthy_http_status_counts` MUST be an empty object

#### Scenario: Healthy probe HTTP statuses are counted

- **WHEN** provider replay status includes requested probes with status `healthy` and integer HTTP statuses
- **THEN** `runtime.probe_summary.healthy_http_status_counts` MUST count those HTTP status values as string keys
- **AND** the counts MUST exclude not-requested probes and non-healthy probes

#### Scenario: Summary view preserves healthy HTTP status counts

- **WHEN** a caller requests provider replay status with `--view summary`
- **THEN** the summary view MUST include `probe_summary.healthy_http_status_counts`
- **AND** the summary view MUST remain read-only and non-lifecycle-managing

### Requirement: Provider replay probe summary SHALL expose failed HTTP status counts

Provider replay status output SHALL include additive `runtime.probe_summary.failed_http_status_counts` derived from requested non-healthy probe HTTP statuses without changing probe execution, daemon lifecycle, scheduler, restart, or provider mutation behavior.

#### Scenario: No requested probes have no failed HTTP status counts

- **WHEN** provider replay status is built without requested probes
- **THEN** `runtime.probe_summary.failed_http_status_counts` MUST be an empty object

#### Scenario: Non-healthy probe HTTP statuses are counted

- **WHEN** provider replay status includes requested probes with non-healthy status and integer HTTP statuses
- **THEN** `runtime.probe_summary.failed_http_status_counts` MUST count those HTTP status values as string keys
- **AND** the counts MUST exclude not-requested probes and healthy probes

#### Scenario: Summary view preserves failed HTTP status counts

- **WHEN** a caller requests provider replay status with `--view summary`
- **THEN** the summary view MUST include `probe_summary.failed_http_status_counts`
- **AND** the summary view MUST remain read-only and non-lifecycle-managing

### Requirement: Provider replay probe summary SHALL expose error sample count

Provider replay status output SHALL include additive `runtime.probe_summary.error_sample_count` derived from the same probe results used for compact `error_samples`, without changing probe execution, daemon lifecycle, scheduler, restart, or provider mutation behavior.

#### Scenario: No requested probes have zero error sample count

- **WHEN** provider replay status is built without requested probes or probe errors
- **THEN** `runtime.probe_summary.error_sample_count` MUST be `0`
- **AND** the status call MUST remain read-only

#### Scenario: Error sample count includes all qualifying probe results

- **WHEN** provider replay status includes probe results that qualify for compact `error_samples`
- **THEN** `runtime.probe_summary.error_sample_count` MUST equal the total qualifying probe result count
- **AND** the count MUST NOT be capped by `runtime.probe_summary.error_sample_limit`
- **AND** `runtime.probe_summary.error_sample_truncated` MUST continue to indicate whether the sample list was truncated

#### Scenario: Summary view preserves error sample count

- **WHEN** a caller requests provider replay status with `--view summary`
- **THEN** the summary view MUST include `probe_summary.error_sample_count`
- **AND** the summary view MUST remain read-only and non-lifecycle-managing

### Requirement: Provider replay probe summary SHALL expose error sample status counts

Provider replay status output SHALL include additive `runtime.probe_summary.error_sample_status_counts` derived from the same probe results used for compact `error_samples`, without changing probe execution, daemon lifecycle, scheduler, restart, or provider mutation behavior.

#### Scenario: No error sample candidates have empty status counts

- **WHEN** provider replay status is built without probe results that qualify for compact error samples
- **THEN** `runtime.probe_summary.error_sample_status_counts` MUST be an empty object
- **AND** the status call MUST remain read-only

#### Scenario: Error sample candidates are counted by status

- **WHEN** provider replay status includes probe results that qualify for compact `error_samples`
- **THEN** `runtime.probe_summary.error_sample_status_counts` MUST count those candidates by normalized probe status
- **AND** the counts MUST use string status keys
- **AND** `runtime.probe_summary.failed_status_counts` MUST keep its requested non-healthy probe semantics

#### Scenario: Summary view preserves error sample status counts

- **WHEN** a caller requests provider replay status with `--view summary`
- **THEN** the summary view MUST include `probe_summary.error_sample_status_counts`
- **AND** the summary view MUST remain read-only and non-lifecycle-managing

### Requirement: Provider replay probe summary SHALL expose error sample probe counts

Provider replay status output SHALL include additive `runtime.probe_summary.error_sample_probe_counts` derived from the same probe results used for compact `error_samples`, without changing probe execution, daemon lifecycle, scheduler, restart, or provider mutation behavior.

#### Scenario: No error sample candidates have empty probe counts

- **WHEN** provider replay status is built without probe results that qualify for compact error samples
- **THEN** `runtime.probe_summary.error_sample_probe_counts` MUST be an empty object
- **AND** the status call MUST remain read-only

#### Scenario: Error sample candidates are counted by probe key

- **WHEN** provider replay status includes probe results that qualify for compact `error_samples`
- **THEN** `runtime.probe_summary.error_sample_probe_counts` MUST count those candidates by probe key
- **AND** the counts MUST use string probe keys
- **AND** the counts MUST NOT depend on whether `error_samples` is truncated

#### Scenario: Summary view preserves error sample probe counts

- **WHEN** a caller requests provider replay status with `--view summary`
- **THEN** the summary view MUST include `probe_summary.error_sample_probe_counts`
- **AND** the summary view MUST remain read-only and non-lifecycle-managing

### Requirement: Provider replay status SHALL summarize probe request coverage

Provider replay status SHALL include additive `runtime.probe_summary.request_coverage_status` derived from existing probe counts without starting sockets, requesting additional probes, mutating provider state, or managing daemon lifecycle.

#### Scenario: No probes requested

- **WHEN** provider replay status is built without any explicit probe result
- **THEN** `runtime.probe_summary.request_coverage_status` MUST be `none`
- **AND** no probe endpoint MUST be requested by this derived field

#### Scenario: Some probes requested

- **WHEN** provider replay status is built with at least one but not all known probe results
- **THEN** `runtime.probe_summary.request_coverage_status` MUST be `partial`
- **AND** the value MUST NOT imply health or readiness

#### Scenario: All probes requested

- **WHEN** provider replay status is built with all known probe results
- **THEN** `runtime.probe_summary.request_coverage_status` MUST be `complete`
- **AND** the value MUST NOT imply all probes are healthy

#### Scenario: CLI summary preserves request coverage status

- **WHEN** a caller runs `provider-replay status --view summary`
- **THEN** the summary payload MUST include `probe_summary.request_coverage_status`
- **AND** the summary payload MUST remain a read-only projection

### Requirement: Provider replay status SHALL expose a primary failed probe hint

Provider replay status SHALL include additive `runtime.probe_summary.primary_failed_probe` derived from the existing failed probe list without starting sockets, requesting additional probes, mutating provider state, or managing daemon lifecycle.

#### Scenario: No failed probes

- **WHEN** provider replay status is built without failed probes
- **THEN** `runtime.probe_summary.primary_failed_probe` MUST be `null`
- **AND** no probe endpoint MUST be requested by this derived field

#### Scenario: Failed probes exist

- **WHEN** provider replay status is built with one or more failed probes
- **THEN** `runtime.probe_summary.primary_failed_probe` MUST equal the first item in `runtime.probe_summary.failed`
- **AND** the value MUST NOT imply recovery, health, or readiness

#### Scenario: CLI summary preserves primary failed probe

- **WHEN** a caller runs `provider-replay status --view summary`
- **THEN** the summary payload MUST include `probe_summary.primary_failed_probe`
- **AND** the summary payload MUST remain a read-only projection

### Requirement: Provider replay status SHALL summarize failed probe reachability

Provider replay status SHALL include additive `runtime.probe_summary.failed_reachability_counts` derived from existing requested non-healthy probe results without starting sockets, requesting additional probes, mutating provider state, or managing daemon lifecycle.

#### Scenario: No failed probes

- **WHEN** provider replay status is built without requested non-healthy probes
- **THEN** `runtime.probe_summary.failed_reachability_counts` MUST be an empty object
- **AND** no probe endpoint MUST be requested by this derived field

#### Scenario: Failed unreachable probes exist

- **WHEN** provider replay status is built with requested non-healthy probes whose `reachable` value is `false`
- **THEN** `runtime.probe_summary.failed_reachability_counts` MUST count those probes under `unreachable`
- **AND** the field MUST NOT include `healthy` or `not_requested` probes

#### Scenario: Failed reachability can be unknown

- **WHEN** provider replay status is built with requested non-healthy probes that omit a boolean `reachable` value
- **THEN** `runtime.probe_summary.failed_reachability_counts` MUST count those probes under `unknown`
- **AND** the field MUST remain a summary over existing probe objects only

#### Scenario: CLI summary preserves failed reachability counts

- **WHEN** a caller runs `provider-replay status --view summary`
- **THEN** the summary payload MUST include `probe_summary.failed_reachability_counts`
- **AND** the summary payload MUST remain a read-only projection

### Requirement: Provider replay status SHALL summarize healthy probe reachability

Provider replay status SHALL include additive `runtime.probe_summary.healthy_reachability_counts` derived from existing requested healthy probe results without starting sockets, requesting additional probes, mutating provider state, or managing daemon lifecycle.

#### Scenario: No healthy probes

- **WHEN** provider replay status is built without requested healthy probes
- **THEN** `runtime.probe_summary.healthy_reachability_counts` MUST be an empty object
- **AND** no probe endpoint MUST be requested by this derived field

#### Scenario: Healthy reachable probes exist

- **WHEN** provider replay status is built with requested healthy probes whose `reachable` value is `true`
- **THEN** `runtime.probe_summary.healthy_reachability_counts` MUST count those probes under `reachable`
- **AND** the field MUST NOT include failed or `not_requested` probes

#### Scenario: Healthy reachability can be unknown

- **WHEN** provider replay status is built with requested healthy probes that omit a boolean `reachable` value
- **THEN** `runtime.probe_summary.healthy_reachability_counts` MUST count those probes under `unknown`
- **AND** the field MUST remain a summary over existing probe objects only

#### Scenario: CLI summary preserves healthy reachability counts

- **WHEN** a caller runs `provider-replay status --view summary`
- **THEN** the summary payload MUST include `probe_summary.healthy_reachability_counts`
- **AND** the summary payload MUST remain a read-only projection

### Requirement: Provider replay status SHALL expose a primary healthy probe hint

Provider replay status SHALL include additive `runtime.probe_summary.primary_healthy_probe` derived from the existing healthy probe list without starting sockets, requesting additional probes, mutating provider state, or managing daemon lifecycle.

#### Scenario: No healthy probes

- **WHEN** provider replay status is built without healthy probes
- **THEN** `runtime.probe_summary.primary_healthy_probe` MUST be `null`
- **AND** no probe endpoint MUST be requested by this derived field

#### Scenario: Healthy probes exist

- **WHEN** provider replay status is built with one or more healthy probes
- **THEN** `runtime.probe_summary.primary_healthy_probe` MUST equal the first item in `runtime.probe_summary.healthy`
- **AND** the value MUST NOT imply full service health, readiness, or endpoint coverage

#### Scenario: CLI summary preserves primary healthy probe

- **WHEN** a caller runs `provider-replay status --view summary`
- **THEN** the summary payload MUST include `probe_summary.primary_healthy_probe`
- **AND** the summary payload MUST remain a read-only projection

### Requirement: Provider replay status SHALL expose a primary not-requested probe hint

Provider replay status SHALL include additive `runtime.probe_summary.primary_not_requested_probe` derived from the existing not-requested probe list without starting sockets, requesting additional probes, mutating provider state, or managing daemon lifecycle.

#### Scenario: All probes requested

- **WHEN** provider replay status is built with every supported probe requested
- **THEN** `runtime.probe_summary.primary_not_requested_probe` MUST be `null`
- **AND** no probe endpoint MUST be requested by this derived field

#### Scenario: Not-requested probes exist

- **WHEN** provider replay status is built with one or more not-requested probes
- **THEN** `runtime.probe_summary.primary_not_requested_probe` MUST equal the first item in `runtime.probe_summary.not_requested`
- **AND** the value MUST NOT imply that the target has been probed, failed, or is unavailable

#### Scenario: CLI summary preserves primary not-requested probe

- **WHEN** a caller runs `provider-replay status --view summary`
- **THEN** the summary payload MUST include `probe_summary.primary_not_requested_probe`
- **AND** the summary payload MUST remain a read-only projection

### Requirement: Provider Replay Primary Requested Probe Summary

Provider replay status SHALL expose a read-only `runtime.probe_summary.primary_requested_probe` field derived from the existing requested probe target list, without requesting additional probes, changing health classification, starting sockets, mutating providers, or managing daemon lifecycle.

#### Scenario: No probe requested

- **GIVEN** provider replay status is requested without any `--probe-*` option
- **WHEN** the probe summary is built
- **THEN** `runtime.probe_summary.primary_requested_probe` MUST be `null`
- **AND** this MUST NOT request or execute any probe.

#### Scenario: Requested probes present

- **GIVEN** provider replay status is requested with one or more explicit probe targets
- **WHEN** the probe summary is built
- **THEN** `runtime.probe_summary.primary_requested_probe` MUST equal the first item in `runtime.probe_summary.requested`
- **AND** this field MUST NOT imply health, readiness, endpoint coverage, or lifecycle control.

#### Scenario: CLI summary includes primary requested probe

- **GIVEN** provider replay status is requested with `--view summary` and one or more explicit probe targets
- **WHEN** the CLI summary view is emitted
- **THEN** `probe_summary.primary_requested_probe` MUST equal the first item in `probe_summary.requested`
- **AND** this field MUST remain a compact read-only diagnostic hint.

### Requirement: Provider Replay Probe Status Key Counts

Provider replay status SHALL expose read-only `runtime.probe_summary` status key-count fields derived from existing probe status count maps without requesting additional probes, changing health classification, starting sockets, mutating providers, or managing daemon lifecycle.

#### Scenario: Probe summary includes status key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `status_counts`
- **THEN** `runtime.probe_summary.status_key_count` MUST equal the number of keys in `status_counts`
- **AND** this field MUST count distinct projected probe status keys, not probes or endpoints.

#### Scenario: Probe summary includes requested status key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `requested_status_counts`
- **THEN** `runtime.probe_summary.requested_status_key_count` MUST equal the number of keys in `requested_status_counts`
- **AND** this field MUST NOT request probes or imply request coverage.

#### Scenario: Probe summary includes failed status key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `failed_status_counts`
- **THEN** `runtime.probe_summary.failed_status_key_count` MUST equal the number of keys in `failed_status_counts`
- **AND** this field MUST NOT imply service readiness, live provider availability, or daemon lifecycle control.

### Requirement: Provider Replay Probe Reachability Key Counts

Provider replay status SHALL expose read-only `runtime.probe_summary` reachability key-count fields derived from existing probe reachability count maps without requesting additional probes, changing health classification, starting sockets, mutating providers, or managing daemon lifecycle.

#### Scenario: Probe summary includes requested reachability key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `requested_reachability_counts`
- **THEN** `runtime.probe_summary.requested_reachability_key_count` MUST equal the number of keys in `requested_reachability_counts`
- **AND** this field MUST count distinct projected requested reachability keys, not probes or endpoints.

#### Scenario: Probe summary includes healthy reachability key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `healthy_reachability_counts`
- **THEN** `runtime.probe_summary.healthy_reachability_key_count` MUST equal the number of keys in `healthy_reachability_counts`
- **AND** this field MUST NOT imply service health, readiness, or endpoint coverage.

#### Scenario: Probe summary includes failed reachability key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `failed_reachability_counts`
- **THEN** `runtime.probe_summary.failed_reachability_key_count` MUST equal the number of keys in `failed_reachability_counts`
- **AND** this field MUST NOT imply live provider availability, daemon lifecycle control, or failure coverage completeness.

### Requirement: Provider Replay Probe HTTP Status Key Counts

Provider replay status SHALL expose read-only `runtime.probe_summary` HTTP status key-count fields derived from existing probe HTTP status count maps without requesting additional probes, changing health classification, starting sockets, mutating providers, or managing daemon lifecycle.

#### Scenario: Probe summary includes requested HTTP status key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `requested_http_status_counts`
- **THEN** `runtime.probe_summary.requested_http_status_key_count` MUST equal the number of keys in `requested_http_status_counts`
- **AND** this field MUST count distinct projected requested HTTP status keys, not probes or endpoints.

#### Scenario: Probe summary includes healthy HTTP status key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `healthy_http_status_counts`
- **THEN** `runtime.probe_summary.healthy_http_status_key_count` MUST equal the number of keys in `healthy_http_status_counts`
- **AND** this field MUST NOT imply service health, readiness, or endpoint coverage.

#### Scenario: Probe summary includes failed HTTP status key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `failed_http_status_counts`
- **THEN** `runtime.probe_summary.failed_http_status_key_count` MUST equal the number of keys in `failed_http_status_counts`
- **AND** this field MUST NOT imply live provider availability, daemon lifecycle control, or failure coverage completeness.

### Requirement: Provider Replay Probe Error Key Counts

Provider replay status SHALL expose read-only `runtime.probe_summary` error key-count fields derived from existing error-code and error-sample count maps without requesting additional probes, exposing full probe payloads, starting sockets, mutating providers, or managing daemon lifecycle.

#### Scenario: Probe summary includes error-code key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `error_code_counts`
- **THEN** `runtime.probe_summary.error_code_key_count` MUST equal the number of keys in `error_code_counts`
- **AND** this field MUST count distinct projected error-code keys, not probes or full error payloads.

#### Scenario: Probe summary includes failed error-code key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `failed_error_code_counts`
- **THEN** `runtime.probe_summary.failed_error_code_key_count` MUST equal the number of keys in `failed_error_code_counts`
- **AND** this field MUST NOT imply failure coverage completeness.

#### Scenario: Probe summary includes error-sample status key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `error_sample_status_counts`
- **THEN** `runtime.probe_summary.error_sample_status_key_count` MUST equal the number of keys in `error_sample_status_counts`
- **AND** this field MUST NOT expose full sample payloads.

#### Scenario: Probe summary includes error-sample probe key count

- **GIVEN** provider replay status is built with any supported probe set
- **WHEN** the probe summary includes `error_sample_probe_counts`
- **THEN** `runtime.probe_summary.error_sample_probe_key_count` MUST equal the number of keys in `error_sample_probe_counts`
- **AND** this field MUST NOT imply health, readiness, live provider availability, or daemon lifecycle control.

### Requirement: Provider replay status SHALL expose a primary unhealthy probe hint

Provider replay status SHALL include additive `runtime.probe_summary.primary_unhealthy_probe` derived from the existing unhealthy probe list without requesting additional probes, changing health classification, starting sockets, mutating providers, scheduling retry/backoff, or managing daemon lifecycle.

#### Scenario: No unhealthy probes exist

- **GIVEN** provider replay status is built with no unhealthy probes
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.primary_unhealthy_probe` MUST be `null`
- **AND** this field MUST NOT request or execute any probe

#### Scenario: Unhealthy probes exist

- **GIVEN** provider replay status is built with one or more unhealthy probes
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.primary_unhealthy_probe` MUST equal the first item in `runtime.probe_summary.unhealthy`
- **AND** existing `unhealthy`, `unhealthy_count`, `failed`, and `primary_failed_probe` fields MUST remain available

#### Scenario: Primary unhealthy probe remains read-only

- **WHEN** a caller inspects provider replay status or summary view
- **THEN** `runtime.probe_summary.primary_unhealthy_probe` MUST NOT start sockets, mutate providers, schedule retry/backoff, or manage daemon lifecycle
- **AND** the field MUST NOT be treated as service health, readiness, endpoint coverage, or production daemon control proof

### Requirement: Provider replay status SHALL expose primary error sample hints

Provider replay status SHALL include additive read-only `runtime.probe_summary.primary_error_sample_probe` and `runtime.probe_summary.primary_error_sample_status` derived from the existing bounded error sample list without requesting additional probes, exposing full probe payloads, starting sockets, mutating providers, scheduling retry/backoff, or managing daemon lifecycle.

#### Scenario: No error samples exist

- **GIVEN** provider replay status is built with no error samples
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.primary_error_sample_probe` MUST be `null`
- **AND** `runtime.probe_summary.primary_error_sample_status` MUST be `null`
- **AND** this field MUST NOT request or execute any probe

#### Scenario: Error samples exist

- **GIVEN** provider replay status is built with one or more error samples
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.primary_error_sample_probe` MUST equal the first sample probe
- **AND** `runtime.probe_summary.primary_error_sample_status` MUST equal the first sample status
- **AND** existing `error_samples`, `error_sample_count`, `error_sample_status_counts`, `error_sample_probe_counts`, and `error_sample_truncated` fields MUST remain available

#### Scenario: Primary error sample hints remain replay-only

- **WHEN** a caller inspects `runtime.probe_summary.primary_error_sample_probe` or `primary_error_sample_status`
- **THEN** these fields MUST NOT start sockets, mutate providers, schedule retry/backoff, request additional probes, or manage daemon lifecycle
- **AND** these fields MUST NOT be treated as provider readiness, endpoint coverage, or live TongDaXin runtime health proof

### Requirement: Provider replay status SHALL expose primary error sample diagnostics

Provider replay status SHALL include additive read-only `runtime.probe_summary.primary_error_sample_error_code` and `runtime.probe_summary.primary_error_sample_http_status` derived from the existing bounded error sample list without requesting additional probes, exposing full probe payloads, starting sockets, mutating providers, scheduling retry/backoff, or managing daemon lifecycle.

#### Scenario: No error samples exist

- **GIVEN** provider replay status is built with no error samples
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.primary_error_sample_error_code` MUST be `null`
- **AND** `runtime.probe_summary.primary_error_sample_http_status` MUST be `null`
- **AND** these fields MUST NOT request or execute any probe

#### Scenario: Error samples include compact diagnostics

- **GIVEN** provider replay status is built with one or more error samples that include compact diagnostic fields
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.primary_error_sample_error_code` MUST equal the first sample error code when present
- **AND** `runtime.probe_summary.primary_error_sample_http_status` MUST equal the first sample HTTP status when present
- **AND** existing `error_samples`, `primary_error_sample_probe`, `primary_error_sample_status`, and error sample count fields MUST remain available

#### Scenario: Primary error sample diagnostics remain replay-only

- **WHEN** a caller inspects `runtime.probe_summary.primary_error_sample_error_code` or `primary_error_sample_http_status`
- **THEN** these fields MUST NOT start sockets, mutate providers, schedule retry/backoff, request additional probes, or manage daemon lifecycle
- **AND** these fields MUST NOT be treated as provider readiness, endpoint coverage, or live TongDaXin runtime health proof

### Requirement: Provider replay status SHALL expose hidden error sample count

Provider replay status SHALL include additive read-only `runtime.probe_summary.error_sample_hidden_count` derived from the existing bounded error sample list and total error sample candidate count without requesting additional probes, exposing full probe payloads, starting sockets, mutating providers, scheduling retry/backoff, or managing daemon lifecycle.

#### Scenario: No error samples are hidden

- **GIVEN** provider replay status is built with zero error samples or with sample candidates within the configured sample limit
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.error_sample_hidden_count` MUST be `0`
- **AND** existing `error_sample_count`, `error_sample_limit`, and `error_sample_truncated` fields MUST remain unchanged

#### Scenario: Error sample candidates are truncated

- **GIVEN** provider replay status is built with more error sample candidates than the configured sample limit
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.error_sample_hidden_count` MUST equal `error_sample_count - len(error_samples)`
- **AND** `runtime.probe_summary.error_sample_truncated` MUST remain `true`

#### Scenario: Hidden error sample count remains replay-only

- **WHEN** a caller inspects `runtime.probe_summary.error_sample_hidden_count`
- **THEN** this field MUST NOT start sockets, mutate providers, schedule retry/backoff, request additional probes, or manage daemon lifecycle
- **AND** this field MUST NOT be treated as provider readiness, endpoint coverage, or live TongDaXin runtime health proof

### Requirement: Provider replay status SHALL expose visible error sample count

Provider replay status SHALL include additive read-only `runtime.probe_summary.error_sample_visible_count` derived from the existing bounded error sample list without requesting additional probes, exposing full probe payloads, starting sockets, mutating providers, scheduling retry/backoff, or managing daemon lifecycle.

#### Scenario: No error samples are visible

- **GIVEN** provider replay status is built with zero visible error samples
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.error_sample_visible_count` MUST be `0`
- **AND** existing `error_sample_count`, `error_sample_hidden_count`, `error_sample_limit`, and `error_sample_truncated` fields MUST remain unchanged

#### Scenario: Error samples are visible

- **GIVEN** provider replay status is built with one or more visible bounded error samples
- **WHEN** the probe summary is returned
- **THEN** `runtime.probe_summary.error_sample_visible_count` MUST equal `len(error_samples)`
- **AND** `runtime.probe_summary.error_sample_count` MUST remain the total candidate count, not the visible list length

#### Scenario: Visible error sample count remains replay-only

- **WHEN** a caller inspects `runtime.probe_summary.error_sample_visible_count`
- **THEN** this field MUST NOT start sockets, mutate providers, schedule retry/backoff, request additional probes, or manage daemon lifecycle
- **AND** this field MUST NOT be treated as provider readiness, endpoint coverage, or live TongDaXin runtime health proof

### Requirement: Provider replay probe summary SHALL expose error sample HTTP status counts

Provider replay status output SHALL include additive read-only `runtime.probe_summary.error_sample_http_status_counts` and `runtime.probe_summary.error_sample_http_status_key_count` fields derived from existing error sample candidate probes with integer HTTP status values, without changing probe execution, replay lifecycle, daemon management, scheduler, restart/backoff, configured endpoints, or provider mutation behavior.

#### Scenario: No error sample HTTP statuses

- **WHEN** provider replay status is built without requested error sample candidates that have integer HTTP status values
- **THEN** `runtime.probe_summary.error_sample_http_status_counts` MUST be an empty object
- **AND** `runtime.probe_summary.error_sample_http_status_key_count` MUST be `0`
- **AND** existing `error_sample_count`, `error_sample_status_counts`, `error_sample_probe_counts`, `error_samples`, and `error_sample_truncated` fields MUST remain available

#### Scenario: Error sample candidates include HTTP statuses

- **WHEN** provider replay status has error sample candidates with integer HTTP status values
- **THEN** `runtime.probe_summary.error_sample_http_status_counts` MUST count those HTTP statuses using string keys
- **AND** `runtime.probe_summary.error_sample_http_status_key_count` MUST equal the number of distinct HTTP status keys
- **AND** the count map MUST be independent of the bounded `error_samples` list truncation
- **AND** existing probe execution, replay lifecycle, daemon management, scheduler, restart/backoff, configured endpoints, and provider mutation behavior MUST remain unchanged

#### Scenario: Summary view includes error sample HTTP status counts

- **WHEN** a caller runs `provider-replay status --view summary` and the underlying probe summary includes `error_sample_http_status_counts`
- **THEN** `summary_view.probe_summary.error_sample_http_status_counts` MUST mirror the detailed runtime probe summary
- **AND** `summary_view.probe_summary.error_sample_http_status_key_count` MUST mirror the detailed runtime probe summary
- **AND** the summary view MUST NOT expose secrets, full probe payloads, daemon lifecycle controls, or provider mutation behavior

### Requirement: Provider replay probe summary SHALL expose error sample reachability counts

Provider replay status output SHALL include additive read-only `runtime.probe_summary.error_sample_reachability_counts` and `runtime.probe_summary.error_sample_reachability_key_count` fields derived from existing error sample candidate probes' normalized reachability buckets, without changing probe execution, replay lifecycle, daemon management, scheduler, restart/backoff, configured endpoints, or provider mutation behavior.

#### Scenario: No error sample reachability candidates

- **WHEN** provider replay status is built without requested error sample candidates
- **THEN** `runtime.probe_summary.error_sample_reachability_counts` MUST be an empty object
- **AND** `runtime.probe_summary.error_sample_reachability_key_count` MUST be `0`
- **AND** existing `error_sample_count`, `error_sample_status_counts`, `error_sample_probe_counts`, `error_samples`, and `error_sample_truncated` fields MUST remain available

#### Scenario: Error sample candidates include reachability states

- **WHEN** provider replay status has error sample candidates with boolean or missing reachability values
- **THEN** `runtime.probe_summary.error_sample_reachability_counts` MUST count `reachable=True` as `reachable`
- **AND** it MUST count `reachable=False` as `unreachable`
- **AND** it MUST count missing or non-boolean reachability as `unknown`
- **AND** `runtime.probe_summary.error_sample_reachability_key_count` MUST equal the number of distinct reachability keys
- **AND** the count map MUST be independent of the bounded `error_samples` list truncation
- **AND** existing probe execution, replay lifecycle, daemon management, scheduler, restart/backoff, configured endpoints, and provider mutation behavior MUST remain unchanged

#### Scenario: Summary view includes error sample reachability counts

- **WHEN** a caller runs `provider-replay status --view summary` and the underlying probe summary includes `error_sample_reachability_counts`
- **THEN** `summary_view.probe_summary.error_sample_reachability_counts` MUST mirror the detailed runtime probe summary
- **AND** `summary_view.probe_summary.error_sample_reachability_key_count` MUST mirror the detailed runtime probe summary
- **AND** the summary view MUST NOT expose secrets, full probe payloads, daemon lifecycle controls, or provider mutation behavior

### Requirement: Provider replay probe summary SHALL expose primary error sample reachability

Provider replay status output SHALL include additive read-only `runtime.probe_summary.primary_error_sample_reachability` derived from the first existing error sample candidate's normalized reachability bucket, without changing `error_samples` payload shape, probe execution, replay lifecycle, daemon management, scheduler, restart/backoff, configured endpoints, or provider mutation behavior.

#### Scenario: No primary error sample reachability exists

- **WHEN** provider replay status is built without error sample candidates
- **THEN** `runtime.probe_summary.primary_error_sample_reachability` MUST be `null`
- **AND** existing primary error sample probe/status/error-code/HTTP-status fields MUST remain `null`
- **AND** existing `error_samples`, `error_sample_count`, and error sample count maps MUST remain available

#### Scenario: First error sample candidate has reachability

- **WHEN** provider replay status has error sample candidates
- **THEN** `runtime.probe_summary.primary_error_sample_reachability` MUST describe the first candidate's reachability as `reachable`, `unreachable`, or `unknown`
- **AND** it MUST use the same first-candidate ordering as `primary_error_sample_probe`
- **AND** `error_samples` payload shape and ordering MUST remain unchanged
- **AND** existing probe execution, replay lifecycle, daemon management, scheduler, restart/backoff, configured endpoints, and provider mutation behavior MUST remain unchanged

#### Scenario: Summary view includes primary error sample reachability

- **WHEN** a caller runs `provider-replay status --view summary` and the underlying probe summary includes `primary_error_sample_reachability`
- **THEN** `summary_view.probe_summary.primary_error_sample_reachability` MUST mirror the detailed runtime probe summary
- **AND** the summary view MUST NOT expose secrets, full probe payloads, daemon lifecycle controls, or provider mutation behavior

### Requirement: Provider replay probe summary SHALL expose error sample summary

Provider replay status probe summaries SHALL include additive read-only `runtime.probe_summary.error_sample_summary` metadata derived from existing bounded error sample diagnostics without exposing full probe payloads, adding probe endpoints, mutating provider state, or managing daemon lifecycle.

#### Scenario: Status probe summary includes compact error sample metadata

- **WHEN** provider replay status probes produce one or more failed probe samples
- **THEN** `runtime.probe_summary.error_sample_summary.count` MUST equal the full error sample count
- **AND** `visible_count`, `hidden_count`, `limit`, and `truncated` MUST match the existing `error_sample_visible_count`, `error_sample_hidden_count`, `error_sample_limit`, and `error_sample_truncated` sibling fields
- **AND** `primary_probe`, `primary_status`, `primary_error_code`, `primary_http_status`, and `primary_reachability` MUST match the existing primary error sample sibling fields
- **AND** hidden counts MUST be non-negative integers
- **AND** the summary MUST NOT expose full probe payloads
- **AND** the summary MUST NOT add probe endpoints, start sockets, mutate provider state, or manage daemon lifecycle

#### Scenario: Status probe summary handles no failed probe samples

- **WHEN** provider replay status probes produce no failed probe samples
- **THEN** `runtime.probe_summary.error_sample_summary.count` MUST be `0`
- **AND** `visible_count` and `hidden_count` MUST be `0`
- **AND** `truncated` MUST be `false`
- **AND** primary fields MUST be `null`
- **AND** the summary MUST remain read-only and MUST NOT be treated as health/readiness proof

### Requirement: Provider replay probe summary SHALL expose request summary

Provider replay status SHALL include additive read-only `runtime.probe_summary.request_summary` metadata derived from existing fixed-probe request coverage fields without starting sockets, executing unrequested probes, managing daemon lifecycle, or enabling write behavior.

#### Scenario: Status includes no-probe request summary

- **WHEN** provider replay status is built without explicit probe requests
- **THEN** `runtime.probe_summary.request_summary.status` MUST be `none`
- **AND** `requested_count` MUST be `0`
- **AND** `not_requested_count` MUST match the number of supported fixed probes
- **AND** `primary_not_requested_probe` MUST remain deterministic
- **AND** existing probe summary sibling fields MUST remain available

#### Scenario: Status includes complete request summary

- **WHEN** provider replay status is built with all fixed probes explicitly requested
- **THEN** `runtime.probe_summary.request_summary.status` MUST be `complete`
- **AND** `requested_count` MUST match `runtime.probe_summary.requested_count`
- **AND** `healthy_count`, `failed_count`, and `unhealthy_count` MUST match the corresponding sibling fields
- **AND** `primary_requested_probe` and `primary_not_requested_probe` MUST match the corresponding sibling fields
- **AND** the object MUST NOT include full probe payloads, error samples, endpoint response bodies, daemon controls, or executable instructions

#### Scenario: Summary view exposes request summary without changing probe behavior

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** the summary view MUST expose `probe_summary.request_summary`
- **AND** the summary view MUST remain read-only and MUST NOT start sockets beyond explicitly requested probes, manage daemon lifecycle, or enable write behavior

### Requirement: Provider replay probe summary SHALL expose health summary

Provider replay status SHALL include additive read-only `runtime.probe_summary.health_summary` metadata derived from existing fixed-probe health fields without starting sockets, executing unrequested probes, managing daemon lifecycle, or enabling write behavior.

#### Scenario: Status includes no-probe health summary

- **WHEN** provider replay status is built without explicit probe requests
- **THEN** `runtime.probe_summary.health_summary.status` MUST be `not_requested`
- **AND** `healthy_count`, `failed_count`, and `unhealthy_count` MUST be `0`
- **AND** primary healthy/failed/unhealthy probe fields MUST be `null`
- **AND** existing probe summary sibling fields MUST remain available

#### Scenario: Status includes degraded health summary

- **WHEN** provider replay status is built with an unhealthy requested probe
- **THEN** `runtime.probe_summary.health_summary.status` MUST match `runtime.probe_summary.status`
- **AND** health/failure counts MUST match the corresponding sibling fields
- **AND** primary healthy/failed/unhealthy probe fields MUST match the corresponding sibling fields
- **AND** the object MUST NOT include full probe payloads, error samples, endpoint response bodies, daemon controls, or executable instructions

#### Scenario: Summary view exposes health summary without changing probe behavior

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** the summary view MUST expose `probe_summary.health_summary`
- **AND** the summary view MUST remain read-only and MUST NOT start sockets beyond explicitly requested probes, manage daemon lifecycle, or enable write behavior

### Requirement: Provider replay probe summary SHALL expose outcome summary

Provider replay status SHALL include additive read-only `runtime.probe_summary.outcome_summary` metadata derived from existing fixed-probe summary fields without starting sockets, executing unrequested probes, changing health classification, managing daemon lifecycle, or enabling write behavior.

#### Scenario: Status includes no-probe outcome summary

- **WHEN** provider replay status is built without explicit probe requests
- **THEN** `runtime.probe_summary.outcome_summary.status` MUST be `not_requested`
- **AND** `request_coverage_status` MUST be `none`
- **AND** `all_probes_requested`, `has_failed_probe`, and `has_unhealthy_probe` MUST be `false`
- **AND** `primary_problem_probe`, `primary_error_sample_probe`, and `primary_error_sample_status` MUST be `null`
- **AND** existing probe summary sibling fields MUST remain available

#### Scenario: Status includes degraded outcome summary

- **WHEN** provider replay status is built with at least one failed or unhealthy requested probe
- **THEN** `runtime.probe_summary.outcome_summary.status` MUST match the existing probe summary status
- **AND** `request_coverage_status` MUST match the existing request coverage status
- **AND** `has_failed_probe` and `has_unhealthy_probe` MUST reflect existing failed and unhealthy counts
- **AND** `primary_problem_probe` MUST identify the first failed, unhealthy, or primary error-sample probe already present in the existing summary

#### Scenario: Summary view exposes outcome summary without changing probe behavior

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** the summary view MUST expose `probe_summary.outcome_summary`
- **AND** the summary view MUST remain read-only and MUST NOT start sockets beyond explicitly requested probes, manage daemon lifecycle, or enable write behavior

### Requirement: Provider replay probe summary SHALL expose primary problem probe

Provider replay status SHALL include additive read-only `runtime.probe_summary.primary_problem_probe` derived only from normalized fixed-probe summary metadata.

#### Scenario: No-probe status reports no primary problem probe

- **WHEN** provider replay status is built without requested probes
- **THEN** `runtime.probe_summary.primary_problem_probe` MUST be `null`
- **AND** `runtime.probe_summary.outcome_summary.primary_problem_probe` MUST also be `null`

#### Scenario: Degraded status reports first problem probe

- **WHEN** provider replay status includes a failed or unhealthy requested probe
- **THEN** `runtime.probe_summary.primary_problem_probe` MUST name the first failed probe when present
- **AND** it MUST match `runtime.probe_summary.outcome_summary.primary_problem_probe`

#### Scenario: Primary problem probe remains advisory

- **WHEN** provider replay status exposes `runtime.probe_summary.primary_problem_probe`
- **THEN** the field MUST NOT indicate that an additional probe, provider mutation, socket start, daemon lifecycle action, restart/backoff, scheduler action, or write behavior was executed
- **AND** the field MUST NOT claim broker readiness, provider readiness, endpoint coverage, or production daemon control

### Requirement: Provider replay probe summary SHALL expose error-sample presence

Provider replay status SHALL include additive read-only `runtime.probe_summary.has_error_sample` derived only from existing normalized probe summary metadata.

#### Scenario: No error samples report false

- **WHEN** provider replay status is built without probe error samples
- **THEN** `runtime.probe_summary.has_error_sample` MUST be `false`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Error samples report true

- **WHEN** provider replay status contains one or more probe error samples
- **THEN** `runtime.probe_summary.has_error_sample` MUST be `true`
- **AND** the field MUST remain consistent with `error_sample_count > 0`

#### Scenario: Error-sample presence remains advisory

- **WHEN** provider replay status exposes `runtime.probe_summary.has_error_sample`
- **THEN** the field MUST NOT indicate that an additional probe, provider mutation, socket start, daemon lifecycle action, restart/backoff, scheduler action, or write behavior was executed
- **AND** the field MUST NOT claim broker readiness, provider readiness, endpoint coverage, or production daemon control

### Requirement: Provider replay probe summary SHALL expose hidden error-sample presence

Provider replay status SHALL include additive read-only `runtime.probe_summary.has_hidden_error_sample` derived only from existing normalized probe summary metadata.

#### Scenario: No hidden error samples report false

- **WHEN** provider replay status has no error samples hidden by the sample limit
- **THEN** `runtime.probe_summary.has_hidden_error_sample` MUST be `false`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Hidden error samples report true

- **WHEN** provider replay status has one or more error samples hidden by the sample limit
- **THEN** `runtime.probe_summary.has_hidden_error_sample` MUST be `true`
- **AND** the field MUST remain consistent with `error_sample_hidden_count > 0`

#### Scenario: Hidden error-sample presence remains advisory

- **WHEN** provider replay status exposes `runtime.probe_summary.has_hidden_error_sample`
- **THEN** the field MUST NOT indicate that an additional probe, provider mutation, socket start, daemon lifecycle action, restart/backoff, scheduler action, or write behavior was executed
- **AND** the field MUST NOT claim broker readiness, provider readiness, endpoint coverage, or production daemon control

### Requirement: Provider replay probe summary SHALL expose visible error-sample presence

Provider replay status SHALL include additive read-only `runtime.probe_summary.has_visible_error_sample` derived only from existing normalized probe summary metadata.

#### Scenario: No visible error samples report false

- **WHEN** provider replay status has no visible error samples in the bounded response
- **THEN** `runtime.probe_summary.has_visible_error_sample` MUST be `false`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Visible error samples report true

- **WHEN** provider replay status has one or more visible error samples in the bounded response
- **THEN** `runtime.probe_summary.has_visible_error_sample` MUST be `true`
- **AND** the field MUST remain consistent with `error_sample_visible_count > 0`

#### Scenario: Visible error-sample presence remains advisory

- **WHEN** provider replay status exposes `runtime.probe_summary.has_visible_error_sample`
- **THEN** the field MUST NOT indicate that an additional probe, provider mutation, socket start, daemon lifecycle action, restart/backoff, scheduler action, or write behavior was executed
- **AND** the field MUST NOT claim broker readiness, provider readiness, endpoint coverage, or production daemon control

### Requirement: Provider replay probe summary SHALL expose healthy probe presence

Provider replay status SHALL include additive read-only `runtime.probe_summary.has_healthy_probe` derived only from existing normalized probe summary metadata.

#### Scenario: No healthy probes report false

- **WHEN** provider replay status has no healthy probes
- **THEN** `runtime.probe_summary.has_healthy_probe` MUST be `false`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Healthy probes report true

- **WHEN** provider replay status has one or more healthy probes
- **THEN** `runtime.probe_summary.has_healthy_probe` MUST be `true`
- **AND** the field MUST remain consistent with `healthy_count > 0`

#### Scenario: Healthy probe presence remains advisory

- **WHEN** provider replay status exposes `runtime.probe_summary.has_healthy_probe`
- **THEN** the field MUST NOT indicate broker readiness, provider readiness, endpoint coverage, daemon lifecycle control, or write capability
- **AND** the field MUST NOT indicate that an additional probe, provider mutation, socket start, restart/backoff, scheduler action, or write behavior was executed

### Requirement: Provider replay probe summary SHALL expose not-requested probe presence

Provider replay status SHALL include additive read-only `runtime.probe_summary.has_not_requested_probe` derived only from existing normalized probe request coverage metadata.

#### Scenario: No not-requested probes report false

- **WHEN** provider replay status has no configured probes or all configured probes were requested
- **THEN** `runtime.probe_summary.has_not_requested_probe` MUST be `false`
- **AND** the field MUST remain consistent with `not_requested_count == 0`

#### Scenario: Not-requested probes report true

- **WHEN** provider replay status has one or more configured probes that were not requested
- **THEN** `runtime.probe_summary.has_not_requested_probe` MUST be `true`
- **AND** the field MUST remain consistent with `not_requested_count > 0`

#### Scenario: Not-requested probe presence remains advisory

- **WHEN** provider replay status exposes `runtime.probe_summary.has_not_requested_probe`
- **THEN** the field MUST NOT indicate provider failure, broker readiness, provider readiness, endpoint coverage, daemon lifecycle control, or write capability
- **AND** the field MUST NOT indicate that an additional probe, provider mutation, socket start, restart/backoff, scheduler action, or write behavior was executed

### Requirement: Provider replay probe summary SHALL expose all-requested coverage

Provider replay status SHALL include additive read-only top-level `runtime.probe_summary.all_probes_requested` derived from the existing probe request coverage calculation.

#### Scenario: No-probe request reports false

- **WHEN** provider replay status has no requested probes
- **THEN** `runtime.probe_summary.all_probes_requested` MUST be `false`
- **AND** the field MUST remain consistent with `outcome_summary.all_probes_requested`

#### Scenario: Partial probe request reports false

- **WHEN** provider replay status has configured probes that were not requested
- **THEN** `runtime.probe_summary.all_probes_requested` MUST be `false`
- **AND** the field MUST remain consistent with `requested_count < total_count`

#### Scenario: Complete probe request reports true

- **WHEN** provider replay status requested every configured probe
- **THEN** `runtime.probe_summary.all_probes_requested` MUST be `true`
- **AND** the field MUST remain consistent with `requested_count == total_count`

#### Scenario: All-requested coverage remains advisory

- **WHEN** provider replay status exposes `runtime.probe_summary.all_probes_requested`
- **THEN** the field MUST NOT indicate broker readiness, provider readiness, endpoint health, endpoint semantic coverage, daemon lifecycle control, or write capability
- **AND** the field MUST NOT indicate that an additional probe, provider mutation, socket start, restart/backoff, scheduler action, or write behavior was executed

### Requirement: Provider replay probe summary SHALL expose requested probe presence

Provider replay status SHALL include additive read-only top-level `runtime.probe_summary.has_requested_probe` derived only from existing normalized probe request metadata.

#### Scenario: No requested probes report false

- **WHEN** provider replay status has no requested probes
- **THEN** `runtime.probe_summary.has_requested_probe` MUST be `false`
- **AND** the field MUST remain consistent with `requested_count == 0`

#### Scenario: Requested probes report true

- **WHEN** provider replay status has one or more requested probes
- **THEN** `runtime.probe_summary.has_requested_probe` MUST be `true`
- **AND** the field MUST remain consistent with `requested_count > 0`

#### Scenario: Requested probe presence remains advisory

- **WHEN** provider replay status exposes `runtime.probe_summary.has_requested_probe`
- **THEN** the field MUST NOT indicate broker readiness, provider readiness, endpoint health, endpoint semantic coverage, daemon lifecycle control, or write capability
- **AND** the field MUST NOT indicate that an additional probe, provider mutation, socket start, restart/backoff, scheduler action, or write behavior was executed

### Requirement: Provider replay probe summary SHALL expose top-level failed probe presence

Provider replay status SHALL include additive read-only top-level `runtime.probe_summary.has_failed_probe` derived only from existing normalized failed probe metadata.

#### Scenario: No failed probes report false

- **WHEN** provider replay status has no failed requested probes
- **THEN** top-level `runtime.probe_summary.has_failed_probe` MUST be `false`
- **AND** the field MUST remain consistent with `failed_count == 0`

#### Scenario: Failed probes report true

- **WHEN** provider replay status has one or more failed requested probes
- **THEN** top-level `runtime.probe_summary.has_failed_probe` MUST be `true`
- **AND** the field MUST remain consistent with `failed_count > 0`
- **AND** the field MUST match `outcome_summary.has_failed_probe`

#### Scenario: Failed probe presence remains advisory

- **WHEN** provider replay status exposes top-level `runtime.probe_summary.has_failed_probe`
- **THEN** the field MUST NOT indicate broker readiness, provider readiness, endpoint semantic coverage, daemon lifecycle control, or write capability
- **AND** the field MUST NOT indicate that an additional probe, provider mutation, socket start, restart/backoff, scheduler action, or write behavior was executed

### Requirement: Provider replay probe summary SHALL expose top-level unhealthy probe presence

Provider replay status SHALL include additive read-only top-level `runtime.probe_summary.has_unhealthy_probe` derived only from existing normalized unhealthy probe metadata.

#### Scenario: No unhealthy probes report false

- **WHEN** provider replay status has no unhealthy probes
- **THEN** top-level `runtime.probe_summary.has_unhealthy_probe` MUST be `false`
- **AND** the field MUST remain consistent with `unhealthy_count == 0`

#### Scenario: Unhealthy probes report true

- **WHEN** provider replay status has one or more unhealthy probes
- **THEN** top-level `runtime.probe_summary.has_unhealthy_probe` MUST be `true`
- **AND** the field MUST remain consistent with `unhealthy_count > 0`
- **AND** the field MUST match `outcome_summary.has_unhealthy_probe`

#### Scenario: Unhealthy probe presence remains advisory

- **WHEN** provider replay status exposes top-level `runtime.probe_summary.has_unhealthy_probe`
- **THEN** the field MUST NOT indicate broker readiness, provider readiness, endpoint semantic coverage, daemon lifecycle control, or write capability
- **AND** the field MUST NOT indicate that an additional probe, provider mutation, socket start, restart/backoff, scheduler action, or write behavior was executed

### Requirement: Provider replay probe summary SHALL expose problem probe presence

Provider replay status SHALL include additive read-only top-level `runtime.probe_summary.has_problem_probe` derived only from existing normalized primary problem probe metadata.

#### Scenario: No problem probe reports false

- **WHEN** provider replay status has no primary problem probe
- **THEN** top-level `runtime.probe_summary.has_problem_probe` MUST be `false`
- **AND** the field MUST remain consistent with `primary_problem_probe is None`

#### Scenario: Problem probe reports true

- **WHEN** provider replay status has a primary problem probe
- **THEN** top-level `runtime.probe_summary.has_problem_probe` MUST be `true`
- **AND** the field MUST remain consistent with `primary_problem_probe is not None`

#### Scenario: Problem probe presence remains advisory

- **WHEN** provider replay status exposes top-level `runtime.probe_summary.has_problem_probe`
- **THEN** the field MUST NOT indicate broker readiness, provider readiness, endpoint semantic coverage, daemon lifecycle control, or write capability
- **AND** the field MUST NOT indicate that an additional probe, provider mutation, socket start, restart/backoff, scheduler action, or write behavior was executed

### Requirement: Provider replay summary view SHALL expose status summary rollup

`provider-replay status --view summary` SHALL include additive read-only `summary_view.status_summary` metadata derived from the already-built provider replay status payload without starting services, executing extra probes, changing detailed status payloads, managing daemon lifecycle, or enabling write behavior.

#### Scenario: Summary view exposes stable replay status rollup

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.status_summary.provider_id` and `transport_mode` MUST match the provider replay status payload
- **AND** `source_kind`, `fixture`, `read_only`, `writes_supported`, `endpoint_count`, `probe_requested`, `requested_probe_count`, `failed_probe_count`, `control_supported`, `managed_operation_count`, `boundary_count`, `runtime_observed`, and `live_runtime_required` MUST be present
- **AND** the summary MUST be derived from existing status, capability, runtime, lifecycle, replay source, and boundary data

#### Scenario: Summary rollup remains read-only and non-authoritative

- **WHEN** the summary rollup is built
- **THEN** it MUST NOT execute probes beyond those explicitly requested by the caller
- **AND** it MUST NOT start, stop, restart, daemonize, schedule, supervise, or otherwise manage a provider process
- **AND** it MUST NOT expose bearer tokens, allowlist members, full endpoint lists, fixture paths, or write-capable controls
- **AND** it MUST NOT claim live provider readiness, production suitability, or workflow execution support

### Requirement: Provider replay health summary SHALL expose probe presence flags

Provider replay status SHALL include additive read-only `runtime.probe_summary.health_summary.has_healthy_probe`, `has_failed_probe`, and `has_unhealthy_probe` fields derived only from existing normalized fixed-probe summary metadata.

#### Scenario: No-probe health summary reports no presence

- **WHEN** provider replay status is built without explicit probe requests
- **THEN** `runtime.probe_summary.health_summary.has_healthy_probe` MUST be `false`
- **AND** `runtime.probe_summary.health_summary.has_failed_probe` MUST be `false`
- **AND** `runtime.probe_summary.health_summary.has_unhealthy_probe` MUST be `false`
- **AND** no probe operation MUST be executed to compute those fields

#### Scenario: Degraded health summary reports failed and unhealthy presence

- **WHEN** provider replay status is built with an unhealthy requested probe
- **THEN** `runtime.probe_summary.health_summary.has_failed_probe` MUST be `true`
- **AND** `runtime.probe_summary.health_summary.has_unhealthy_probe` MUST be `true`
- **AND** each field MUST match the corresponding top-level `runtime.probe_summary` presence field
- **AND** the summary MUST NOT include full probe payloads, endpoint response bodies, daemon controls, or executable instructions

#### Scenario: Summary view exposes health presence flags without changing probe behavior

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** the summary view MUST expose the same `probe_summary.health_summary` presence flags
- **AND** the command MUST remain read-only and MUST NOT start sockets beyond explicitly requested probes, manage daemon lifecycle, schedule supervision, or enable write behavior

### Requirement: Provider replay probe summary SHALL expose advisory summary

Provider replay status SHALL include additive read-only `runtime.probe_summary.advisory_summary` metadata derived only from existing normalized fixed-probe summary fields.

#### Scenario: No-probe status exposes an advisory summary

- **WHEN** provider replay status is built without explicit probe requests
- **THEN** `runtime.probe_summary.advisory_summary.status` MUST be `not_requested`
- **AND** `runtime.probe_summary.advisory_summary.request_coverage_status` MUST be `none`
- **AND** `runtime.probe_summary.advisory_summary.has_requested_probe` MUST be `false`
- **AND** `runtime.probe_summary.advisory_summary.has_problem_probe` MUST be `false`
- **AND** no probe operation MUST be executed to compute the advisory summary

#### Scenario: Degraded status exposes problem advisory hints

- **WHEN** provider replay status is built with an unhealthy requested probe
- **THEN** `runtime.probe_summary.advisory_summary.status` MUST match `runtime.probe_summary.status`
- **AND** the advisory counts and presence flags MUST match the corresponding sibling fields
- **AND** `runtime.probe_summary.advisory_summary.primary_problem_probe` MUST match the corresponding sibling field
- **AND** the advisory summary MUST include a read-only boundary marker
- **AND** the advisory summary MUST NOT include full probe payloads, endpoint response bodies, daemon controls, or executable instructions

#### Scenario: Summary view exposes advisory summary without changing probe behavior

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** the summary view MUST expose `probe_summary.advisory_summary`
- **AND** the command MUST remain read-only and MUST NOT start sockets beyond explicitly requested probes, manage daemon lifecycle, schedule supervision, or enable write behavior

### Requirement: Provider replay status summary SHALL expose probe advisory fields

The provider replay status summary view SHALL include read-only probe advisory fields in `summary_view.status_summary` derived only from the already-built `runtime.probe_summary`.

#### Scenario: Summary view exposes compact probe advisory posture

- **WHEN** a caller requests `provider-replay status --view summary` with explicit probe flags
- **THEN** `summary_view.status_summary.probe_status` MUST match `runtime.probe_summary.advisory_summary.status`
- **AND** `summary_view.status_summary.probe_request_coverage_status` MUST match `runtime.probe_summary.advisory_summary.request_coverage_status`
- **AND** `summary_view.status_summary.has_problem_probe` MUST match `runtime.probe_summary.advisory_summary.has_problem_probe`
- **AND** `summary_view.status_summary.primary_problem_probe` MUST match `runtime.probe_summary.advisory_summary.primary_problem_probe`

#### Scenario: Summary view probe advisory fields remain read-only

- **WHEN** the summary view exposes probe advisory fields
- **THEN** the detailed `status` payload and copied `probe_summary` MUST remain available
- **AND** the command MUST NOT execute additional probes, start sockets beyond explicitly requested probes, manage daemon lifecycle, schedule supervision, or enable write behavior
- **AND** the fields MUST NOT be treated as readiness, broker availability, endpoint coverage, workflow readiness, or write-capability proof

### Requirement: Provider replay daemon lifecycle design SHALL define future control boundaries

The provider replay daemon lifecycle design SHALL define future start, stop, lifecycle status, restart, and backoff boundaries without changing the current provider-replay runtime behavior.

#### Scenario: Current status remains non-lifecycle-managing

- **WHEN** a caller uses the existing provider-replay status, probe, or summary view commands
- **THEN** the commands MUST remain read-only lifecycle boundary inspections
- **AND** they MUST NOT start, stop, restart, daemonize, schedule, supervise, or apply backoff
- **AND** lifecycle support fields MUST continue to distinguish configured replay capability from managed daemon control

#### Scenario: Future start is explicit and ownership-tracked

- **WHEN** a future lifecycle controller introduces provider-replay start behavior
- **THEN** start MUST require an explicit operator action and explicit replay config
- **AND** it MUST record ownership metadata sufficient to distinguish controller-owned replay processes from arbitrary already-running services
- **AND** it MUST NOT imply live provider, broker, workflow, or write readiness

#### Scenario: Future stop fails closed without ownership proof

- **WHEN** a future lifecycle controller introduces provider-replay stop behavior
- **THEN** stop MUST target only a process that the controller can prove it owns
- **AND** it MUST NOT kill arbitrary processes discovered only by port, probe, or HTTP reachability
- **AND** absence of an owned process MUST be reported as a lifecycle boundary, not hidden as successful daemon control

#### Scenario: Future lifecycle status separates ownership from reachability

- **WHEN** a future lifecycle controller reports daemon lifecycle status
- **THEN** status MUST distinguish configured replay capability, owned process state, observed HTTP health, and stale or missing ownership metadata
- **AND** a reachable probe alone MUST NOT be treated as proof that the lifecycle controller owns the process
- **AND** status MUST remain safe to run without mutating provider or daemon state

#### Scenario: Future restart and backoff remain explicit lifecycle control

- **WHEN** a future lifecycle controller introduces restart or supervised backoff behavior
- **THEN** restart MUST require ownership proof and explicit lifecycle control
- **AND** read-only status, probe, summary, catalog discovery, or validation commands MUST NOT trigger restart
- **AND** backoff policy MUST expose retry count, delay window, last failure reason, and whether the next retry is pending or blocked
- **AND** automatic restart/backoff MUST be opt-in and bounded rather than implied by the current replay status surface

### Requirement: Provider replay lifecycle status SHALL expose ownership summary

Provider replay lifecycle status SHALL include additive read-only `lifecycle.ownership_summary` metadata that distinguishes current non-ownership from future daemon lifecycle control.

#### Scenario: Detailed status reports no lifecycle ownership

- **WHEN** provider replay status is built with the current non-lifecycle-managing implementation
- **THEN** `lifecycle.ownership_summary.ownership_status` MUST be `not_managed`
- **AND** `lifecycle.ownership_summary.owned_process` MUST be `false`
- **AND** `lifecycle.ownership_summary.state_file_present` MUST be `false`
- **AND** `lifecycle.ownership_summary.state_file_stale` MUST be `false`
- **AND** `lifecycle.ownership_summary.control_allowed` MUST be `false`
- **AND** the summary MUST identify the status source as a configured boundary rather than ownership proof

#### Scenario: Summary view projects lifecycle ownership without adding control

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.lifecycle.ownership_summary` MUST match the detailed lifecycle ownership summary
- **AND** the existing detailed `status` payload MUST remain available
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, write state files, read process tables, infer ownership from ports, or enable write behavior

#### Scenario: Ownership summary remains a boundary declaration

- **WHEN** lifecycle ownership summary is present
- **THEN** it MUST NOT be treated as readiness, broker availability, endpoint coverage, workflow readiness, or write-capability proof
- **AND** future lifecycle control MUST still require explicit ownership metadata before stop or restart operations can be allowed

### Requirement: Provider replay lifecycle status SHALL expose control summary

Provider replay lifecycle status SHALL include additive read-only `lifecycle.control_summary` metadata that identifies current lifecycle control operations as unavailable.

#### Scenario: Detailed status reports lifecycle control is unsupported

- **WHEN** provider replay status is built with the current non-lifecycle-managing implementation
- **THEN** `lifecycle.control_summary.control_status` MUST be `unsupported`
- **AND** `lifecycle.control_summary.control_allowed` MUST be `false`
- **AND** `lifecycle.control_summary.available_operations` MUST be empty
- **AND** `lifecycle.control_summary.blocked_operations` MUST include `start`, `stop`, `restart`, and `backoff`
- **AND** `lifecycle.control_summary.blocking_reason` MUST identify lifecycle control as not implemented
- **AND** the summary MUST state that ownership proof and operator action are required before future lifecycle control

#### Scenario: Summary view projects lifecycle control without adding control

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.lifecycle.control_summary` MUST match the detailed lifecycle control summary
- **AND** the existing detailed `status` payload MUST remain available
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, write state files, read process tables, infer ownership from ports, or enable write behavior

#### Scenario: Control summary remains a boundary declaration

- **WHEN** lifecycle control summary is present
- **THEN** it MUST NOT be treated as readiness, broker availability, endpoint coverage, workflow readiness, or write-capability proof
- **AND** future lifecycle control MUST still require explicit implementation and ownership proof before stop or restart operations can be allowed

### Requirement: Provider replay status summary SHALL expose lifecycle control fields

The provider replay status summary view SHALL include read-only lifecycle ownership/control fields in `summary_view.status_summary` derived only from the already-built lifecycle summary metadata.

#### Scenario: Summary view exposes compact lifecycle control posture

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.status_summary.lifecycle_ownership_status` MUST match `summary_view.lifecycle.ownership_summary.ownership_status`
- **AND** `summary_view.status_summary.lifecycle_owned_process` MUST match `summary_view.lifecycle.ownership_summary.owned_process`
- **AND** `summary_view.status_summary.lifecycle_control_status` MUST match `summary_view.lifecycle.control_summary.control_status`
- **AND** `summary_view.status_summary.lifecycle_blocking_reason` MUST match `summary_view.lifecycle.control_summary.blocking_reason`

#### Scenario: Summary lifecycle fields remain read-only

- **WHEN** the summary view exposes lifecycle control fields
- **THEN** the detailed `status` payload and `summary_view.lifecycle` MUST remain available
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, write state files, read process tables, infer ownership from ports, or enable write behavior
- **AND** the fields MUST NOT be treated as readiness, broker availability, endpoint coverage, workflow readiness, or write-capability proof

### Requirement: Provider replay lifecycle status SHALL expose operation summary

Provider replay lifecycle status SHALL include additive read-only `lifecycle.operation_summary` metadata that describes current lifecycle operation availability per operation.

#### Scenario: Detailed status reports all lifecycle operations blocked

- **WHEN** provider replay status is built with the current non-lifecycle-managing implementation
- **THEN** `lifecycle.operation_summary.operation_count` MUST be `4`
- **AND** `lifecycle.operation_summary.available_count` MUST be `0`
- **AND** `lifecycle.operation_summary.blocked_count` MUST be `4`
- **AND** `lifecycle.operation_summary.operations` MUST include entries for `start`, `stop`, `restart`, and `backoff`
- **AND** each current operation entry MUST report `status=blocked`, `implemented=false`, and `blocking_reason=lifecycle_control_not_implemented`

#### Scenario: Summary view projects lifecycle operation summary without adding control

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.lifecycle.operation_summary` MUST match the detailed lifecycle operation summary
- **AND** the existing detailed `status` payload MUST remain available
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, write state files, read process tables, infer ownership from ports, or enable write behavior

#### Scenario: Operation summary remains a boundary declaration

- **WHEN** lifecycle operation summary is present
- **THEN** it MUST NOT be treated as readiness, broker availability, endpoint coverage, workflow readiness, or write-capability proof
- **AND** future lifecycle control MUST still require explicit implementation and ownership proof where required before operations can be allowed

### Requirement: Provider replay status summary SHALL expose lifecycle operation counts

The provider replay status summary view SHALL include read-only lifecycle operation count fields in `summary_view.status_summary` derived only from the already-built lifecycle operation summary metadata.

#### Scenario: Summary view exposes compact lifecycle operation counts

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.status_summary.lifecycle_operation_count` MUST match `summary_view.lifecycle.operation_summary.operation_count`
- **AND** `summary_view.status_summary.lifecycle_available_operation_count` MUST match `summary_view.lifecycle.operation_summary.available_count`
- **AND** `summary_view.status_summary.lifecycle_blocked_operation_count` MUST match `summary_view.lifecycle.operation_summary.blocked_count`
- **AND** `summary_view.status_summary.lifecycle_primary_blocked_operation` MUST identify the first blocked lifecycle operation

#### Scenario: Summary lifecycle operation counts remain read-only

- **WHEN** the summary view exposes lifecycle operation count fields
- **THEN** the detailed `status` payload and `summary_view.lifecycle.operation_summary` MUST remain available
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, write state files, read process tables, infer ownership from ports, or enable write behavior
- **AND** the fields MUST NOT be treated as readiness, broker availability, endpoint coverage, workflow readiness, or write-capability proof

### Requirement: Provider replay lifecycle status SHALL expose backoff summary

Provider replay lifecycle status SHALL include additive read-only `lifecycle.backoff_summary` metadata that describes current supervised backoff state as unavailable.

#### Scenario: Detailed status reports backoff is not configured

- **WHEN** provider replay status is built with the current non-lifecycle-managing implementation
- **THEN** `lifecycle.backoff_summary.backoff_status` MUST be `not_configured`
- **AND** `lifecycle.backoff_summary.enabled` MUST be `false`
- **AND** `lifecycle.backoff_summary.policy` MUST be `not_managed`
- **AND** `lifecycle.backoff_summary.retry_count` MUST be `0`
- **AND** `lifecycle.backoff_summary.next_retry_status` MUST be `not_scheduled`
- **AND** `lifecycle.backoff_summary.next_retry_pending` MUST be `false`
- **AND** the summary MUST identify lifecycle control as not implemented

#### Scenario: Summary view projects lifecycle backoff without adding control

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.lifecycle.backoff_summary` MUST match the detailed lifecycle backoff summary
- **AND** the existing detailed `status` payload MUST remain available
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, write state files, read process tables, infer ownership from ports, run timers, or enable write behavior

#### Scenario: Backoff summary remains a boundary declaration

- **WHEN** lifecycle backoff summary is present
- **THEN** it MUST NOT be treated as readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry
- **AND** future supervised backoff MUST still require explicit implementation, opt-in policy, bounded retry rules, and ownership proof where required

### Requirement: Provider replay lifecycle status SHALL expose supervision summary

Provider replay lifecycle status SHALL include additive read-only `lifecycle.supervision_summary` metadata that describes current supervisor and process tracking state as unavailable.

#### Scenario: Detailed status reports provider replay is not supervised

- **WHEN** provider replay status is built with the current non-lifecycle-managing implementation
- **THEN** `lifecycle.supervision_summary.supervision_status` MUST be `not_supervised`
- **AND** `lifecycle.supervision_summary.supervisor_configured` MUST be `false`
- **AND** `lifecycle.supervision_summary.supervisor_type` MUST be `none`
- **AND** `lifecycle.supervision_summary.managed_process_count` MUST be `0`
- **AND** `lifecycle.supervision_summary.active_process_count` MUST be `0`
- **AND** `lifecycle.supervision_summary.desired_state` MUST be `unmanaged`
- **AND** `lifecycle.supervision_summary.observed_state` MUST be `not_observed`
- **AND** `lifecycle.supervision_summary.process_identity_status` MUST be `not_tracked`
- **AND** `lifecycle.supervision_summary.state_file_status` MUST be `not_configured`
- **AND** `lifecycle.supervision_summary.pid_status` MUST be `not_tracked`
- **AND** the summary MUST identify lifecycle control as not implemented

#### Scenario: Summary view projects lifecycle supervision without adding control

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.lifecycle.supervision_summary` MUST match the detailed lifecycle supervision summary
- **AND** the existing detailed `status` payload MUST remain available
- **AND** the command MUST NOT start, stop, restart, daemonize, supervise, write or read state files, track pids, read process tables, infer ownership from ports, run timers, schedule retries, or enable write behavior

#### Scenario: Supervision summary remains a boundary declaration

- **WHEN** lifecycle supervision summary is present
- **THEN** it MUST NOT be treated as process ownership proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry
- **AND** future supervisor behavior MUST still require explicit implementation, process ownership proof, lifecycle state storage, and opt-in control semantics

### Requirement: Provider replay status summary SHALL expose supervision rollup fields

Provider replay status summary view SHALL expose compact read-only supervision rollup fields derived from `lifecycle.supervision_summary`.

#### Scenario: Summary status includes supervision scalars

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.status_summary.lifecycle_supervision_status` MUST match `status.lifecycle.supervision_summary.supervision_status`
- **AND** `summary_view.status_summary.lifecycle_supervisor_configured` MUST match `status.lifecycle.supervision_summary.supervisor_configured`
- **AND** `summary_view.status_summary.lifecycle_desired_state` MUST match `status.lifecycle.supervision_summary.desired_state`
- **AND** `summary_view.status_summary.lifecycle_observed_state` MUST match `status.lifecycle.supervision_summary.observed_state`
- **AND** `summary_view.status_summary.lifecycle_process_identity_status` MUST match `status.lifecycle.supervision_summary.process_identity_status`
- **AND** the existing detailed `status` payload and nested `summary_view.lifecycle.supervision_summary` MUST remain available

#### Scenario: Supervision rollup is non-executing

- **WHEN** supervision rollup fields are present
- **THEN** the command MUST NOT start, stop, restart, daemonize, supervise, track pids, read or write state files, inspect process tables, infer ownership from ports, run timers, schedule retries, or enable write behavior
- **AND** the rollup MUST NOT be treated as process ownership proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry

### Requirement: Provider replay lifecycle status SHALL expose statefile boundary

Provider replay lifecycle status SHALL include additive read-only `lifecycle.statefile_summary` metadata derived from the optional `lifecycle_state_file` config value.

#### Scenario: Detailed status reports no statefile is configured

- **WHEN** provider replay status is built without `lifecycle_state_file`
- **THEN** `lifecycle.statefile_summary.statefile_status` MUST be `not_configured`
- **AND** `lifecycle.statefile_summary.configured` MUST be `false`
- **AND** `lifecycle.statefile_summary.path_provided` MUST be `false`
- **AND** `lifecycle.statefile_summary.read_attempted` MUST be `false`
- **AND** `lifecycle.statefile_summary.write_attempted` MUST be `false`
- **AND** `lifecycle.statefile_summary.present` MUST be `null`
- **AND** `lifecycle.statefile_summary.stale` MUST be `null`
- **AND** the summary MUST identify lifecycle control as not implemented

#### Scenario: Detailed status reports configured statefile is not inspected

- **WHEN** provider replay status is built with `lifecycle_state_file`
- **THEN** `lifecycle.statefile_summary.statefile_status` MUST be `configured_not_inspected`
- **AND** `lifecycle.statefile_summary.configured` MUST be `true`
- **AND** `lifecycle.statefile_summary.path_provided` MUST be `true`
- **AND** `lifecycle.statefile_summary.read_attempted` MUST be `false`
- **AND** `lifecycle.statefile_summary.write_attempted` MUST be `false`
- **AND** `lifecycle.statefile_summary.present` MUST be `null`
- **AND** `lifecycle.statefile_summary.stale` MUST be `null`
- **AND** the command MUST NOT read, write, create, delete, lock, or validate the statefile path on disk

#### Scenario: Config-check summary reports statefile boundary without inspection

- **WHEN** a caller requests `provider-replay config-check --view summary` for a config containing `lifecycle_state_file`
- **THEN** `summary_view.lifecycle_state_file_provided` MUST be `true`
- **AND** `summary_view.statefile_inspected` MUST be `false`
- **AND** `summary_view.statefile_written` MUST be `false`
- **AND** `summary_view.daemon_lifecycle_managed` MUST remain `false`
- **AND** the command MUST NOT start, stop, restart, daemonize, supervise, probe runtime, read process tables, infer ownership from ports, or enable write behavior

#### Scenario: Statefile boundary is non-authoritative

- **WHEN** statefile boundary metadata is present
- **THEN** it MUST NOT be treated as process ownership proof, stale-state proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry
- **AND** future lifecycle statefile behavior MUST still require explicit implementation, ownership proof, state schema, stale detection policy, and opt-in control semantics

### Requirement: Provider replay CLI SHALL expose non-executing lifecycle control plans

Provider replay CLI SHALL expose a read-only `lifecycle-plan` command that reports the current blocked plan for lifecycle operations without executing them.

#### Scenario: Lifecycle plan command parses an operation

- **WHEN** a caller parses `provider-replay lifecycle-plan --config <path> --operation stop`
- **THEN** the command MUST be accepted as a provider replay subcommand
- **AND** the parsed operation MUST be `stop`
- **AND** the default view MUST be `detailed`

#### Scenario: Detailed lifecycle plan reports blocked operation without dispatch

- **WHEN** a caller requests `provider-replay lifecycle-plan --operation stop`
- **THEN** the result MUST include `plan.execution_mode=non_executing_lifecycle_plan`
- **AND** `plan.operation` MUST be `stop`
- **AND** `plan.operation_status` MUST be `blocked`
- **AND** `plan.dispatch_executed` MUST be `false`
- **AND** `plan.control_allowed` MUST be `false`
- **AND** `plan.lifecycle_control_status` MUST be `unsupported`
- **AND** `plan.blocking_reason` MUST identify lifecycle control as not implemented
- **AND** `plan.statefile_configured` MUST reflect the config-derived statefile boundary
- **AND** `plan.supervision_status` MUST reflect lifecycle supervision status

#### Scenario: Summary lifecycle plan projects compact blocked state

- **WHEN** a caller requests `provider-replay lifecycle-plan --operation restart --view summary`
- **THEN** `summary_view.mode` MUST be `lifecycle-plan`
- **AND** `summary_view.operation` MUST be `restart`
- **AND** `summary_view.operation_status` MUST be `blocked`
- **AND** `summary_view.dispatch_executed` MUST be `false`
- **AND** `summary_view.control_allowed` MUST be `false`
- **AND** `summary_view.lifecycle_control_status` MUST be `unsupported`
- **AND** `summary_view.blocking_reason` MUST identify lifecycle control as not implemented

#### Scenario: Lifecycle plan is non-executing

- **WHEN** lifecycle plan output is produced
- **THEN** the command MUST NOT start, stop, restart, daemonize, supervise, probe runtime, inspect process tables, infer ownership from ports, read or write statefiles, schedule retries, or enable write behavior
- **AND** the plan MUST NOT be treated as process ownership proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry

### Requirement: Provider replay CLI SHALL expose read-only lifecycle statefile checks

Provider replay CLI SHALL expose a read-only `lifecycle-state-check` command that validates configured lifecycle statefile shape and freshness without granting lifecycle control.

#### Scenario: Lifecycle statefile check command parses

- **WHEN** a caller parses `provider-replay lifecycle-state-check --config <path>`
- **THEN** the command MUST be accepted as a provider replay subcommand
- **AND** the default view MUST be `detailed`
- **AND** the default stale threshold MUST be present

#### Scenario: Detailed check reports configured valid stale statefile

- **WHEN** a caller requests `provider-replay lifecycle-state-check` for a configured statefile using schema `tdx.provider_replay.lifecycle_state.v1`
- **THEN** the result MUST include `statefile_check.check_status=valid`
- **AND** `statefile_check.read_attempted` MUST be `true`
- **AND** `statefile_check.write_attempted` MUST be `false`
- **AND** `statefile_check.schema_valid` MUST be `true`
- **AND** `statefile_check.provider_id_matches` MUST be `true`
- **AND** `statefile_check.stale` MUST reflect the configured stale threshold
- **AND** `statefile_check.control_allowed` MUST be `false`

#### Scenario: Detailed check reports missing statefile

- **WHEN** a caller requests `provider-replay lifecycle-state-check` for a configured path that does not exist
- **THEN** `statefile_check.check_status` MUST be `missing`
- **AND** `statefile_check.read_attempted` MUST be `true`
- **AND** `statefile_check.write_attempted` MUST be `false`
- **AND** `statefile_check.exists` MUST be `false`
- **AND** lifecycle control MUST remain disallowed

#### Scenario: Detailed check reports not configured without filesystem IO

- **WHEN** a caller requests `provider-replay lifecycle-state-check` without `lifecycle_state_file`
- **THEN** `statefile_check.check_status` MUST be `not_configured`
- **AND** `statefile_check.read_attempted` MUST be `false`
- **AND** `statefile_check.write_attempted` MUST be `false`
- **AND** lifecycle control MUST remain disallowed

#### Scenario: Summary check projects compact statefile diagnostics

- **WHEN** a caller requests `provider-replay lifecycle-state-check --view summary`
- **THEN** `summary_view.mode` MUST be `lifecycle-state-check`
- **AND** `summary_view.check_status` MUST match the detailed statefile check
- **AND** `summary_view.schema_valid` MUST match the detailed statefile check
- **AND** `summary_view.provider_id_matches` MUST match the detailed statefile check
- **AND** `summary_view.stale` MUST match the detailed statefile check
- **AND** `summary_view.control_allowed` MUST be `false`

#### Scenario: Statefile check is non-authoritative

- **WHEN** lifecycle statefile check output is produced
- **THEN** the command MUST NOT start, stop, restart, daemonize, supervise, probe runtime, inspect process tables, infer ownership from ports, write or lock statefiles, schedule retries, or enable write behavior
- **AND** a valid check MUST NOT be treated as process ownership proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry

### Requirement: Provider replay lifecycle plans SHALL expose opt-in statefile diagnostics

Provider replay lifecycle plans SHALL optionally include compact read-only lifecycle statefile diagnostics when explicitly requested.

#### Scenario: Lifecycle plan parses opt-in statefile diagnostics flag

- **WHEN** a caller parses `provider-replay lifecycle-plan --config <path> --operation stop --include-statefile-check`
- **THEN** the command MUST be accepted
- **AND** `include_statefile_check` MUST be `true`
- **AND** the default stale threshold MUST be present

#### Scenario: Detailed lifecycle plan includes statefile diagnostics when requested

- **WHEN** a caller requests `provider-replay lifecycle-plan --operation stop --include-statefile-check`
- **THEN** `plan.statefile_check_included` MUST be `true`
- **AND** `plan.statefile_check_status` MUST reflect the read-only statefile check result
- **AND** `plan.statefile_schema_valid` MUST reflect the read-only statefile check result
- **AND** `plan.statefile_provider_id_matches` MUST reflect the read-only statefile check result
- **AND** `plan.statefile_stale` MUST reflect the read-only statefile check result
- **AND** `plan.statefile_diagnostics.control_allowed` MUST be `false`
- **AND** `plan.dispatch_executed` MUST remain `false`
- **AND** `plan.control_allowed` MUST remain `false`

#### Scenario: Lifecycle plan excludes statefile diagnostics by default

- **WHEN** a caller requests `provider-replay lifecycle-plan --operation stop` without `--include-statefile-check`
- **THEN** `plan.statefile_check_included` MUST be `false`
- **AND** `plan.statefile_diagnostics` MUST be `null`
- **AND** the command MUST NOT read the configured lifecycle statefile

#### Scenario: Lifecycle plan summary projects statefile diagnostics

- **WHEN** a caller requests `provider-replay lifecycle-plan --operation restart --include-statefile-check --view summary`
- **THEN** `summary_view.statefile_check_included` MUST be `true`
- **AND** `summary_view.statefile_check_status` MUST match the detailed plan
- **AND** `summary_view.statefile_schema_valid` MUST match the detailed plan
- **AND** `summary_view.statefile_provider_id_matches` MUST match the detailed plan
- **AND** `summary_view.statefile_stale` MUST match the detailed plan
- **AND** `summary_view.control_allowed` MUST remain `false`

#### Scenario: Statefile diagnostics remain non-authoritative

- **WHEN** lifecycle plan statefile diagnostics are present
- **THEN** the command MUST NOT start, stop, restart, daemonize, supervise, probe runtime, inspect process tables, infer ownership from ports, write or lock statefiles, schedule retries, or enable write behavior
- **AND** valid diagnostics MUST NOT be treated as process ownership proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry

### Requirement: Provider replay CLI SHALL expose read-only lifecycle readiness summaries

Provider replay CLI SHALL expose a read-only `lifecycle-readiness` command that summarizes current lifecycle control readiness without executing lifecycle control.

#### Scenario: Lifecycle readiness command parses

- **WHEN** a caller parses `provider-replay lifecycle-readiness --config <path>`
- **THEN** the command MUST be accepted as a provider replay subcommand
- **AND** the default view MUST be `detailed`
- **AND** statefile diagnostics MUST be opt-in
- **AND** the default stale threshold MUST be present

#### Scenario: Detailed readiness reports blocked control by default

- **WHEN** a caller requests `provider-replay lifecycle-readiness` without statefile diagnostics
- **THEN** `readiness.ready` MUST be `false`
- **AND** `readiness.readiness_status` MUST be `blocked`
- **AND** `readiness.control_allowed` MUST be `false`
- **AND** `readiness.dispatch_executed` MUST be `false`
- **AND** `readiness.statefile_check_included` MUST be `false`
- **AND** `readiness.missing_requirements` MUST include lifecycle controller, owned process identity, supervisor loop, operator opt-in control, and valid lifecycle statefile requirements
- **AND** the command MUST NOT read the configured lifecycle statefile by default

#### Scenario: Detailed readiness can count valid statefile diagnostic prerequisite

- **WHEN** a caller requests `provider-replay lifecycle-readiness --include-statefile-check` for a valid, non-stale, provider-matched statefile
- **THEN** `readiness.statefile_check_included` MUST be `true`
- **AND** `readiness.statefile_check_status` MUST be `valid`
- **AND** `readiness.statefile_schema_valid` MUST be `true`
- **AND** `readiness.statefile_provider_id_matches` MUST be `true`
- **AND** `readiness.statefile_stale` MUST be `false`
- **AND** `readiness.satisfied_requirements` MUST include `valid_lifecycle_statefile`
- **AND** `readiness.ready` MUST still be `false`
- **AND** `readiness.control_allowed` MUST still be `false`

#### Scenario: Summary readiness projects compact blocked state

- **WHEN** a caller requests `provider-replay lifecycle-readiness --include-statefile-check --view summary`
- **THEN** `summary_view.mode` MUST be `lifecycle-readiness`
- **AND** `summary_view.ready` MUST be `false`
- **AND** `summary_view.readiness_status` MUST be `blocked`
- **AND** `summary_view.control_allowed` MUST be `false`
- **AND** `summary_view.missing_requirement_count` MUST match the detailed readiness
- **AND** `summary_view.statefile_check_status` MUST match the detailed readiness

#### Scenario: Readiness summary is non-authoritative

- **WHEN** lifecycle readiness output is produced
- **THEN** the command MUST NOT start, stop, restart, daemonize, supervise, probe runtime, inspect process tables, infer ownership from ports, write or lock statefiles, schedule retries, or enable write behavior
- **AND** valid diagnostics MUST NOT be treated as process ownership proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry

### Requirement: Provider replay lifecycle SHALL write ownership statefiles under lock

Provider replay lifecycle support SHALL provide an internal statefile writer that records daemon ownership metadata under an exclusive lock and atomically replaces the configured lifecycle statefile.

#### Scenario: Ownership statefile write records canonical metadata

- **WHEN** a caller writes a provider replay lifecycle statefile for a config with `lifecycle_state_file`
- **THEN** the write result MUST report `write_status` as `written`
- **AND** the writer MUST acquire and release a lock file associated with the statefile
- **AND** the persisted JSON MUST include the lifecycle schema version, provider id, integer pid, state, owner token, generation, config hash, and updated timestamp
- **AND** the persisted JSON MUST NOT include the raw provider token
- **AND** the write MUST be atomic from the caller contract perspective

#### Scenario: Existing lock blocks statefile mutation

- **WHEN** the associated lock file already exists
- **THEN** the write result MUST report `write_status` as `locked`
- **AND** the writer MUST NOT replace the existing statefile
- **AND** the result MUST include a lock error
- **AND** the command MUST NOT start, stop, restart, supervise, probe runtime, or inspect processes

#### Scenario: Read-only statefile diagnostics report ownership fields when present

- **WHEN** a caller checks a statefile written by the lifecycle statefile writer
- **THEN** diagnostics MUST report the owner token, generation, config hash, and config hash match status
- **AND** the check result MUST remain read-only
- **AND** the check result MUST NOT treat a valid statefile as daemon readiness, process ownership proof, supervisor health, write capability, or lifecycle control permission

#### Scenario: Statefile ownership layer is not daemon lifecycle control

- **WHEN** lifecycle statefile ownership helpers are available
- **THEN** provider replay lifecycle status and readiness MUST still avoid claiming daemon start/stop/restart, long-running supervision, restart/backoff scheduling, process liveness, port ownership, real provider management, broker readiness, workflow readiness, or write readiness

### Requirement: Provider replay CLI SHALL expose managed daemon start/status/stop

Provider replay lifecycle control SHALL expose a minimal managed daemon control surface that can start, inspect, and stop a tool-owned replay daemon using the lifecycle statefile ownership layer.

#### Scenario: Managed daemon start records owned process metadata

- **WHEN** a caller starts a managed provider replay daemon with a config containing `lifecycle_state_file`
- **THEN** the implementation MUST launch `provider-replay serve --config <path>` as a background process
- **AND** it MUST write a lifecycle statefile with the spawned PID, owner token, generation, config hash, and `state=running`
- **AND** it MUST return the owner token and process id
- **AND** it MUST NOT start a second daemon when a valid statefile already points to a running owned PID

#### Scenario: Managed daemon status is read-only

- **WHEN** a caller requests managed daemon status
- **THEN** the implementation MUST read lifecycle statefile diagnostics
- **AND** it MUST evaluate PID liveness only when a valid PID is present
- **AND** it MUST report whether the managed daemon is running
- **AND** it MUST NOT mutate the statefile, start a process, stop a process, supervise, or schedule retries

#### Scenario: Managed daemon stop requires matching owner token

- **WHEN** a caller stops a managed provider replay daemon
- **THEN** the implementation MUST require an owner token
- **AND** it MUST validate provider id, config hash, owner token, and PID liveness before termination
- **AND** it MUST send a termination signal only to the recorded owned PID
- **AND** it MUST write a `state=stopping` lifecycle statefile after sending termination
- **AND** it MUST reject missing or mismatched owner tokens without signaling a process

#### Scenario: Managed daemon control remains bounded

- **WHEN** managed daemon start/status/stop are available
- **THEN** the implementation MUST NOT claim long-running supervision, automatic restart/backoff, port ownership inference, real provider management, broker readiness, workflow readiness, or write readiness

### Requirement: Provider replay CLI SHALL expose a foreground managed daemon supervisor

Provider replay lifecycle control SHALL expose a foreground supervisor that owns one managed replay daemon process, refreshes lifecycle heartbeat state, and records child exit state without automatic restart/backoff.

#### Scenario: Supervisor writes heartbeat state while child is running

- **WHEN** a caller runs the managed daemon supervisor
- **THEN** the supervisor MUST launch `provider-replay serve --config <path>`
- **AND** it MUST write a lifecycle statefile with `state=supervising`
- **AND** it MUST refresh the statefile heartbeat while the child remains running
- **AND** it MUST return the owner token, child PID, heartbeat count, and command metadata

#### Scenario: Supervisor records child exit without restart

- **WHEN** the supervised child exits
- **THEN** the supervisor MUST write a lifecycle statefile with `state=exited`
- **AND** it MUST report the child exit code
- **AND** it MUST NOT relaunch the child
- **AND** it MUST NOT schedule restart/backoff

#### Scenario: Supervisor interruption records stopping state

- **WHEN** the supervisor is interrupted while the child is running
- **THEN** it MUST attempt to terminate the child
- **AND** it MUST write a lifecycle statefile with `state=stopping`
- **AND** it MUST return an interrupted supervisor status

#### Scenario: Supervisor control remains bounded

- **WHEN** the foreground supervisor is available
- **THEN** the implementation MUST NOT claim automatic restart/backoff, recovery policy, port ownership inference, real provider management, broker readiness, workflow readiness, or write readiness

### Requirement: Provider replay daemon supervisor SHALL support opt-in restart/backoff

The provider replay foreground supervisor SHALL support a bounded, opt-in restart/backoff policy for non-zero child exits while keeping no-restart behavior as the default.

#### Scenario: Default supervisor does not restart

- **WHEN** the supervisor runs without an explicit restart policy
- **THEN** child exit MUST be recorded as `state=exited`
- **AND** the supervisor MUST NOT relaunch the child
- **AND** no backoff MUST be scheduled

#### Scenario: On-failure policy retries after backoff

- **WHEN** `restart_policy=on-failure` and a child exits with a non-zero code while restart budget remains
- **THEN** the supervisor MUST write `state=backoff`
- **AND** it MUST wait for the configured backoff seconds
- **AND** it MUST relaunch the child
- **AND** it MUST report restart and backoff counts

#### Scenario: Restart exhaustion records failed state

- **WHEN** a child exits with a non-zero code after restart budget is exhausted
- **THEN** the supervisor MUST write `state=failed`
- **AND** it MUST report `supervisor_status=restart_exhausted`
- **AND** it MUST NOT relaunch the child again

#### Scenario: Restart/backoff remains bounded

- **WHEN** restart/backoff is available
- **THEN** the implementation MUST NOT persist restart budget across separate supervisor invocations, infer ownership from ports, validate real provider readiness, assert broker/workflow/write readiness, or enable restart unless explicitly requested

### Requirement: Provider replay daemon status SHALL expose process ownership diagnostics

Provider replay daemon status SHALL expose a read-only process ownership diagnostic that combines statefile validity, owner token, config hash, PID liveness, and optional process identity match.

#### Scenario: Owned process is reported when all ownership checks pass

- **WHEN** statefile diagnostics are valid, provider id matches, config hash matches, owner token matches when expected, PID is live, and optional process identity matches
- **THEN** ownership diagnostics MUST report `ownership_status=owned`
- **AND** `owned_process` MUST be `true`
- **AND** daemon status `control_allowed` MAY be true for the managed replay daemon

#### Scenario: Process ownership diagnostics explain missing ownership

- **WHEN** the PID is not live, owner token mismatches, config hash mismatches, statefile is stale, or optional process identity mismatches
- **THEN** ownership diagnostics MUST report a specific non-owned status
- **AND** `owned_process` MUST be `false`
- **AND** diagnostics MUST remain read-only

#### Scenario: Lifecycle readiness can count owned process identity

- **WHEN** lifecycle readiness includes ownership diagnostics proving `owned_process=true`
- **THEN** `owned_process_identity` MUST move from missing requirements to satisfied requirements
- **AND** readiness MUST remain blocked until the remaining lifecycle requirements are satisfied

#### Scenario: Ownership diagnostics remain bounded

- **WHEN** ownership diagnostics are available
- **THEN** the implementation MUST NOT kill processes, infer ownership from ports, enable default command-line inspection, recover real providers, or assert broker/workflow/write readiness

