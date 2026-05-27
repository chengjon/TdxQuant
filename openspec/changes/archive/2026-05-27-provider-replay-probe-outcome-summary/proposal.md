## Why

`provider-replay status` already exposes detailed fixed-probe counts, request coverage, health summary, and bounded error samples. Callers that only need a compact read-only outcome still have to combine several sibling fields themselves, which increases the chance of treating partial or failed probes as a stronger runtime signal than they are.

## What Changes

- Add an additive `runtime.probe_summary.outcome_summary` object to provider replay status.
- Derive the object only from existing normalized fixed-probe metadata: status, request coverage, counts, primary probe hints, and primary error-sample hints.
- Keep the field read-only and non-authoritative: it must not start sockets, request additional probes, manage daemon lifecycle, enable writes, or prove live provider readiness.

## Impact

- Affected spec: `tdx-provider-transport-replay-service`
- Affected code: provider replay status summary builder, CLI summary projection, focused tests, and `FUNCTION_TREE.md` E-06 registry evidence/boundary.
