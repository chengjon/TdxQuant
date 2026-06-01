## Why

D-07 `confirm_current` already routes through `execute_pingan_confirm_current`, but its pre-dispatch setup still lives inline in the manager method: profile resolution, timeout overrides, broker-readiness guard, lifecycle owner-lock guard, rejection context, dispatch context, and execution request construction.

Order paths now have a preparation helper. Aligning confirm-current with that shape reduces drift between D-07 and D-08 seams while keeping the real UI lookup/click/result-dialog dispatch in the manager callsite.

## What Changes

- Add an internal `PingAnConfirmCurrentExecutionPreparation` object.
- Add `TdxTradeManager._prepare_pingan_confirm_current_execution(...)` for profile, guard, context, and request preparation.
- Route `confirm_current` through the preparation helper before its manager-owned desktop dispatch body.
- Preserve existing public manager, CLI, task, catalog, guard, metadata, dispatch, finalize, and audit behavior.
- Update `FUNCTION_TREE.md` D-07 evidence and boundary.

## Impact

- Behavior: no intended external behavior change.
- Risk: low to medium; the change touches confirm-current setup but leaves UI dispatch body and execution seam behavior intact.
- Boundary: internal locality only; no new public API, CLI, task, catalog, workflow builder, desktop primitive, live readiness, or production trading readiness claim.
