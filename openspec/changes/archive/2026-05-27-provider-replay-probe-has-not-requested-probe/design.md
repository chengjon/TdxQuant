# Design: Provider Replay Probe Has Not Requested Probe

## Context

E-06 remains `[部分实现]`: provider replay exposes rich read-only status metadata, but it is not a production daemon lifecycle manager.
Recent slices added compact presence flags for failed, unhealthy, error-sample, visible/hidden error-sample, and healthy probe states.
Request coverage has equivalent normalized metadata through `not_requested`, `not_requested_count`, and `primary_not_requested_probe`, but no single explicit presence flag.

## Design

Expose `runtime.probe_summary.has_not_requested_probe` as `bool(not_requested)`.
The field is top-level under `probe_summary`, next to counts and primary probe hints.
It must remain consistent with `not_requested_count > 0` and must not alter `request_summary`, `outcome_summary`, `health_summary`, probe ordering, probe execution, or degraded/healthy classification.

Tests cover:

- no-probe-request status reports `true` because configured probes were not requested;
- partially requested configured probes report `true`;
- all requested configured probes report `false`;
- CLI summary view preserves the field.

## Non-Goals

- No new provider replay endpoints or probes.
- No socket start, process management, scheduler, restart/backoff, or daemon lifecycle control.
- No provider mutation or write capability.
- No readiness claim; this only reports that at least one configured probe was not requested.
