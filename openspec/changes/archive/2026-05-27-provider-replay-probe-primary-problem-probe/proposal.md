# Proposal: Provider Replay Primary Problem Probe

## Why

`provider-replay status --probe-*` already derives `outcome_summary.primary_problem_probe`, but compact consumers must know to read the nested outcome object. E-06 remains partial and benefits from one top-level advisory identity hint that points to the first probe needing attention while preserving the existing non-executing provider replay boundary.

## What Changes

- Add additive read-only `runtime.probe_summary.primary_problem_probe`.
- Derive it from the same normalized fixed-probe ordering already used by `outcome_summary.primary_problem_probe`: first failed probe, else first unhealthy probe, else first error-sample probe.
- Keep the field advisory only: it must not start sockets, request additional probes, manage daemon lifecycle, enable writes, or prove live provider readiness.

## Impact

- Affected spec: `tdx-provider-transport-replay-service`
- Affected code: provider replay status summary builder, focused provider replay/CLI tests, and `FUNCTION_TREE.md` E-06 registry evidence/boundary.
