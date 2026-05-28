# provider replay lifecycle statefile boundary design

## Context

Provider replay is still a foreground, fixture-backed replay service. It does not run a daemon supervisor and does not own any process identity. A statefile path can be useful as future configuration, but in the current implementation it must remain non-authoritative metadata.

## Design

Add optional `ProviderTransportReplayConfig.lifecycle_state_file`.

Detailed status adds `lifecycle.statefile_summary`:

- `statefile_status`: `configured_not_inspected` when a path is configured, otherwise `not_configured`
- `configured`: boolean
- `path_provided`: boolean
- `read_attempted`: `false`
- `write_attempted`: `false`
- `present`: `null`
- `stale`: `null`
- `ownership_source`: `not_available`
- `control_allowed`: `false`
- `blocked`: `true`
- `blocking_reason`: `lifecycle_control_not_implemented`
- `boundary`: `read_only_statefile_config_boundary; no_statefile_io`

Config-check summary adds:

- `lifecycle_state_file_provided`
- `statefile_inspected`: `false`
- `statefile_written`: `false`

The status builder must not call filesystem APIs for the statefile path. The config-check command must not inspect, create, update, delete, or lock a statefile.

## Boundaries

- This change parses and reports a configured statefile path boundary only.
- It does not implement lifecycle state storage, pid ownership, stale detection, locks, process table inspection, port ownership inference, start/stop/restart, daemonization, supervisor loops, retry timers, or automatic recovery.
- It does not prove readiness, live provider availability, broker readiness, workflow readiness, endpoint coverage, or write capability.
