# Design: Provider Replay Probe Has Requested Probe

## Context

E-06 remains `[部分实现]`: provider replay exposes read-only replay/status metadata, but it is not a production daemon lifecycle manager.
Recent slices added compact top-level flags for healthy probes, not-requested probes, and all-requested coverage.
The requested side still lacks a symmetric top-level boolean that tells compact consumers whether this status request asked for any probe at all.

## Design

Expose top-level `runtime.probe_summary.has_requested_probe` as `bool(requested)`.
The field must remain consistent with `requested_count > 0` and must not alter `request_summary`, `health_summary`, `outcome_summary`, probe ordering, probe execution, or degraded/healthy classification.

Tests cover:

- no-probe-request status reports `false`;
- partially requested configured probes report `true`;
- all requested configured probes report `true`;
- CLI summary view preserves the field.

## Non-Goals

- No new provider replay endpoints or probes.
- No socket start, process management, scheduler, restart/backoff, or daemon lifecycle control.
- No provider mutation or write capability.
- No readiness claim; this only reports whether the current status request requested at least one configured probe.
