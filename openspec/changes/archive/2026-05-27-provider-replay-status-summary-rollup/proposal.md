## Why

`provider-replay status --view summary` already exposes nested replay source, capability, runtime, lifecycle, probe, and boundary fields. Callers that only need a stable registry-style status still have to combine several nested objects, which makes it easy to over-read the fake provider as managed runtime readiness instead of a read-only replay surface.

## What Changes

- Add an additive top-level `summary_view.status_summary` object for `provider-replay status --view summary`.
- Derive the object only from the already-built provider replay status payload: provider identity, transport/source shape, read/write capability flags, endpoint/probe/control/boundary counts, and runtime observation flags.
- Keep the field read-only and non-authoritative: it must not execute extra probes, start or stop services, manage daemon lifecycle, enable writes, or claim fake provider production readiness.

## Impact

- Affected spec: `tdx-provider-transport-replay-service`
- Affected code: provider replay CLI summary projection, focused CLI tests, and `FUNCTION_TREE.md` E-06 registry evidence/boundary.
