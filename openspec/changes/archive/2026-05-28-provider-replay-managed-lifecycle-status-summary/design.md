## Context

The runtime already exposes `provider-replay daemon start|status|stop`, `provider-replay daemon supervise`, opt-in restart/backoff, statefile ownership locking, and process ownership diagnostics. The remaining inconsistency is the static lifecycle metadata returned by `build_provider_transport_replay_status()`: it still describes lifecycle control as unavailable even when `lifecycle_state_file` is configured.

## Goals / Non-Goals

**Goals:**

- Make lifecycle status truthfully report that managed replay daemon lifecycle controls are available when `lifecycle_state_file` is configured.
- Preserve the old unsupported posture when no lifecycle statefile path is configured.
- Keep the status output read-only and bounded.

**Non-Goals:**

- No process start/stop/supervise/restart execution from status.
- No statefile read/write or process table inspection from status.
- No port ownership inference.
- No real TongDaXin provider lifecycle management.
- No broker, workflow, write-capability, or production readiness claim.

## Decisions

- Use `lifecycle_state_file` as the configuration gate. The managed daemon commands require this path for state coordination, so status can report the lifecycle surface as available only when the path exists in config.
- Report static availability separately from authorization. Detailed status may list `start`, `status`, `stop`, `supervise`, and `restart_backoff` as available, but `control_allowed` remains `false` because authorization still requires an explicit daemon command and, for stop/restart, ownership diagnostics.
- Keep existing summary derivation. `_build_provider_replay_status_summary_view()` already derives counts and lifecycle compact fields from detailed lifecycle metadata, so implementation should update the detailed payload first and only add summary fields if needed for clarity.

## Risks / Trade-offs

- [Risk] A reader may treat available lifecycle operations as proof that a provider is running. -> Mitigation: keep `runtime_observed` probe-derived, keep `control_allowed=false`, and keep boundaries explicit.
- [Risk] Existing tests assert the old unsupported posture. -> Mitigation: preserve old behavior for configs without `lifecycle_state_file` and add new coverage for configured lifecycle statefiles.
