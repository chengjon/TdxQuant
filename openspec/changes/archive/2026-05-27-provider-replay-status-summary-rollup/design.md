## Context

E-06 tracks the daemon fake provider surface. The current implementation is intentionally constrained: it provides a replay-only HTTP surface, status/config summaries, and opt-in probes, but not daemon lifecycle control. `provider-replay status --view summary` has useful nested objects, yet it lacks one compact field that records the status shape as a registry summary.

## Design

Add `summary_view.status_summary` in `_build_provider_replay_status_summary_view`. The object is a pure projection from existing values already present in the detailed provider replay status and existing summary view inputs.

The field should include stable scalar or count values:

- `provider_id`, `transport_mode`, `source_kind`, and `fixture`
- `read_only` and `writes_supported`
- `endpoint_count`
- `probe_requested`, `requested_probe_count`, and `failed_probe_count`
- `control_supported` and `managed_operation_count`
- `boundary_count`
- `runtime_observed` and `live_runtime_required`

## Boundaries

- Do not add lifecycle commands such as start, stop, restart, daemonize, schedule, supervise, or backoff.
- Do not execute additional probes while building `status_summary`; use the already requested probe summary only.
- Do not expose bearer tokens, allowlist members, full endpoint lists, or fixture paths.
- Do not change the detailed `status` payload shape beyond preserving existing fields.
- Do not claim live provider readiness or workflow execution.
