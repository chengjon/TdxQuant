# Change: Provider Replay Probe Error Samples

## Why

`provider-replay status` now exposes probe status counts, target lists, and error-code counts. Operators still need a bounded sample of unhealthy probe details in the compact status payload, without reading every raw probe object or interpreting the fake provider as lifecycle-managed.

## What Changes

- Add `runtime.probe_summary.error_samples`, a bounded read-only list derived from existing normalized probe objects.
- Add `runtime.probe_summary.error_sample_limit` and `runtime.probe_summary.error_sample_truncated`.
- Preserve the existing `provider-replay status --view summary` behavior by carrying the additive probe summary fields through the existing summary projection.

## Out of Scope

- No new probe endpoints, HTTP calls, or retry behavior.
- No socket start, daemon start/stop, scheduler, restart, reconnect, or lifecycle control.
- No secret token, allowlist member, or full fixture-path exposure.
