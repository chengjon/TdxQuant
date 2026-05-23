# Design: Provider Replay Probe Summary

## Context

`build_provider_transport_replay_status()` normalizes every optional probe input
before building the status payload. The normalized objects already carry a stable
`enabled` flag and `status` string, including `not_requested` for omitted probes.

## Decisions

### Derive Summary Locally

Add a small helper that receives the normalized probe mapping and returns a
read-only rollup. The helper does not perform HTTP requests and does not inspect
credentials.

The summary fields are:

- `status`: `not_requested`, `healthy`, or `degraded`
- `requested_count`: number of probes whose status is not `not_requested`
- `healthy_count`: number of requested probes whose status is `healthy`
- `failed_count`: number of requested probes whose status is not `healthy`
- `not_requested_count`: number of omitted probes
- `requested`: requested probe keys
- `unhealthy`: requested probe keys that are not healthy
- `boundary`: fixed text that states the rollup is read-only and does not manage
  daemon lifecycle

### Keep Existing Probe Objects Stable

The individual probe objects remain the source evidence. The summary is a
consumer convenience projection, not a replacement.

### Preserve Lifecycle Boundary

The status object still reports `foreground_process`, `start_stop_managed=false`,
`daemon_managed=false`, and `restart_policy=not_managed`. The summary must not
imply that provider replay status starts a socket or observes a daemon unless an
explicit probe result was supplied by the caller.

## Risks

- Consumers may mistake the rollup for a daemon health check. Mitigation: include
  an explicit `boundary` string and update `FUNCTION_TREE.md` with the same
  limitation.
