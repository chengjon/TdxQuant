## Why

D-08 PingAn order execution now has an internal execution seam and module-owned result builders, but the four order manager callsites still repeat the same preparation sequence:

- build an effective profile
- evaluate submission idempotency
- evaluate max-price risk
- apply broker-readiness and lifecycle owner-lock guards
- build `PingAnExecutionRequest`
- build the order handler bundle

This is still execution-seam knowledge spread across callsites. A narrow preparation helper reduces drift risk while keeping desktop dispatch code in the manager path where the UIA/HID adapter call is still assembled.

## What Changes

- Add a `PingAnOrderExecutionPreparation` object to describe prepared order execution inputs.
- Add a manager helper that returns the prepared request, idempotency, risk gate, effective profile, and handler bundle for order paths.
- Route buy/sell/submit-once manager callsites through the preparation helper before desktop dispatch.
- Preserve existing public manager, CLI, task, catalog, idempotency, risk-gate, lifecycle, broker-readiness, dispatch, finalize, and audit behavior.
- Update `FUNCTION_TREE.md` D-08 evidence and boundary.

## Impact

- Behavior: no intended external behavior change.
- Risk: low to medium; the repeated preparation logic touches all order callsites, but focused PingAn route tests already cover request/idempotency/risk-gate behavior.
- Boundary: internal locality only; no new public API, CLI, task, catalog, workflow builder, desktop primitive, live readiness, or production trading readiness claim.
