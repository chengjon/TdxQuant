# Design: Provider Replay Probe All Requested Flag

## Context

E-06 remains `[部分实现]`: provider replay exposes read-only replay/status metadata, but it is not a production daemon lifecycle manager.
Request coverage currently appears as `request_coverage_status`, requested/not-requested counts, `has_not_requested_probe`, and nested `outcome_summary.all_probes_requested`.
The top-level summary has no single boolean for “this status request covered every configured probe.”

## Design

Expose top-level `runtime.probe_summary.all_probes_requested` using the existing expression `bool(total_count and requested_count == total_count)`.
This preserves the current non-vacuous behavior: no configured/requested probes does not become “all requested.”
The field must match `outcome_summary.all_probes_requested` and must not alter `request_summary`, `health_summary`, `outcome_summary`, probe ordering, probe execution, or degraded/healthy classification.

Tests cover:

- no-probe-request status reports `false`;
- partially requested configured probes report `false`;
- all requested configured probes report `true`;
- CLI summary view preserves the field.

## Non-Goals

- No new provider replay endpoints or probes.
- No socket start, process management, scheduler, restart/backoff, or daemon lifecycle control.
- No provider mutation or write capability.
- No readiness claim; this only reports request coverage for the current status payload.
