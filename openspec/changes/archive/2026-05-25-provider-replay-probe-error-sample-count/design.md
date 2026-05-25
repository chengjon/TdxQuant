## Design

The provider replay probe summary builder already maintains `error_sample_count` while deciding whether a probe qualifies for the compact `error_samples` list. This change exposes that existing internal counter as `runtime.probe_summary.error_sample_count`.

The count uses the current sample qualification rule:

- A probe qualifies when its status is neither `healthy` nor `not_requested`.
- A probe also qualifies when it has a non-empty string `error_code`.
- The exposed count is not limited by `PROVIDER_REPLAY_PROBE_ERROR_SAMPLE_LIMIT`.

`summary_view.probe_summary` already mirrors the detailed `runtime.probe_summary`, so no separate summary transformation is required beyond ensuring tests assert the field is preserved.

## Boundaries

- The count is a compact diagnostic scalar, not the full error payload.
- The count does not imply health coverage or failure coverage.
- The count does not start, stop, restart, daemonize, schedule, supervise, or mutate a provider.
