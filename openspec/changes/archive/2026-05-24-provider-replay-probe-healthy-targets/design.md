## Overview

Add an additive `runtime.probe_summary.healthy` list to the provider replay status rollup. The list mirrors the existing `requested` and `unhealthy` target lists, but includes targets whose existing probe result has `status == "healthy"`.

## Data Shape

`runtime.probe_summary.healthy` is a deterministic list of probe target names ordered by `PROVIDER_REPLAY_STATUS_PROBE_KEYS`.

- No requested probes: `healthy` is `[]`.
- All requested probes healthy: `healthy` contains every requested target.
- Mixed results: `healthy` contains only targets with `status == "healthy"` while `unhealthy` contains requested non-healthy targets.

The field is also visible in CLI `provider-replay status --view summary` because that summary already copies `runtime.probe_summary`.

## Boundary

The healthy target list is a derived read-only rollup. It does not perform probes by itself, does not start the replay HTTP server, does not manage daemon lifecycle, does not schedule restarts, and does not imply live-market readiness.
