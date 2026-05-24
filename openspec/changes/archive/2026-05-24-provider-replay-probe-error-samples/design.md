# Design: Provider Replay Probe Error Samples

## Overview

`_build_provider_replay_probe_summary()` already iterates over fixed probe targets. During that pass it can collect compact samples for probes with an `error_code` or unhealthy status.

## Data Shape

Each item in `runtime.probe_summary.error_samples` contains compact fields only when present:

- `probe`: fixed probe key such as `health_probe`.
- `status`: normalized probe status.
- `error_code`: normalized error code.
- `http_status`: normalized HTTP status.

The list is capped by `PROVIDER_REPLAY_PROBE_ERROR_SAMPLE_LIMIT`.

## Projection

`provider-replay status --view summary` deep-copies `runtime.probe_summary`, so the summary view will mirror the detailed probe summary without exposing full probe objects.

## Compatibility

The change is additive. Existing status fields and probe execution behavior remain unchanged.
