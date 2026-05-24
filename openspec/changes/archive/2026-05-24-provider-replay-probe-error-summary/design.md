# Design: Provider Replay Probe Error Summary

## Overview

`_build_provider_replay_probe_summary()` already iterates over normalized probe results to derive status counts and target lists. During the same pass, it will count non-empty `error_code` values into a sorted `error_code_counts` object.

## Data Shape

`runtime.probe_summary.error_code_counts` is:

- `{}` when no requested probe reports an error code.
- A sorted map of `{error_code: count}` when unhealthy or otherwise error-classified probe objects include error codes.

## Projection

The CLI `provider-replay status --view summary` already deep-copies `runtime.probe_summary` into `summary_view.probe_summary`, so no separate summary builder shape is needed beyond tests that pin the additive field.

## Compatibility

The field is additive and read-only. Existing status consumers can ignore it, and no existing key changes semantics.
