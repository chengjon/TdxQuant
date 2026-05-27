# Design: Provider Replay Primary Problem Probe

## Context

The provider replay probe summary already exposes ordered probe lists, status counts, primary failed/unhealthy/error-sample hints, and nested `outcome_summary.primary_problem_probe`. CLI summary views copy `runtime.probe_summary` without executing commands or probing beyond the caller's requested flags.

## Design

Expose a top-level `runtime.probe_summary.primary_problem_probe` using the existing derived `primary_problem_probe` local value:

- failed probes take precedence because they represent requested probes that did not return healthy status;
- unhealthy probes remain the next fallback for unexpected but normalized probe outcomes;
- error samples are the last fallback so transport/error visibility can still point to a probe when failed/unhealthy ordering is otherwise empty.

The value is `null` when no failed, unhealthy, or error-sample probe is present. The nested `outcome_summary.primary_problem_probe` remains unchanged, and tests assert both shapes stay aligned for degraded status and null for no-probe status.

## Non-Goals

- Do not add new probe endpoints or request unrequested probes.
- Do not change health/degraded classification or count maps.
- Do not start sockets, manage daemon lifecycle, restart/backoff, schedule probes, mutate providers, or enable write behavior.
- Do not claim broker readiness, provider readiness, endpoint coverage, or production daemon control.
