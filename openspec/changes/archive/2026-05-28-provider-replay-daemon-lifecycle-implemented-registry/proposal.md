## Why

E-06 has accumulated implemented evidence for the replay fake provider lifecycle surface: fake HTTP provider, probes, managed daemon start/status/stop, statefile locking, supervisor loop, restart/backoff, process ownership diagnostics, managed lifecycle status, and lifecycle readiness gating. `FUNCTION_TREE.md` still keeps E-06 at `[部分实现]` and the main row boundary still says there is no start/stop/restart/backoff lifecycle control, which is now stale.

## What Changes

- Promote E-06 in `FUNCTION_TREE.md` from `[部分实现]` to `[已实现]`.
- Rewrite the E-06 main row evidence and boundary so the implemented scope is explicit and current.
- Preserve the boundary that E-06 is a replay fake provider managed lifecycle, not real TongDaXin provider lifecycle, broker/workflow readiness, market runtime availability, or write capability.
- Keep the existing supplemental E-06 registration notes as historical detail.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-function-tree-registry`: E-06 may be registered as implemented when all replay fake provider lifecycle evidence is present and the boundary prevents overclaiming runtime/provider/write readiness.

## Impact

- Affected registry: `FUNCTION_TREE.md`.
- Verification: FUNCTION_TREE registry validator, OpenSpec validation, focused provider replay/CLI tests, and whitespace checks.
