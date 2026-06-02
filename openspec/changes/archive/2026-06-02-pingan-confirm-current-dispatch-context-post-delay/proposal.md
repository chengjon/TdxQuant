# PingAn Confirm-Current Dispatch Context Post Delay

## Why

D-07 confirm-current has an internal execution seam, preparation helper, dispatch result builder, and handler bundle. The remaining dispatch closure still reads `confirm_post_delay` directly from `effective_profile` while the other confirm/result dialog options already come from `PingAnConfirmCurrentDispatchContext`.

Moving `confirm_post_delay` into the confirm-current dispatch context keeps all profile-derived dispatch timing inputs in one internal object. This tightens the seam without moving desktop primitives or changing public behavior.

## What Changes

- Extend `PingAnConfirmCurrentDispatchContext` with `confirm_post_delay`.
- Populate that field in `_prepare_pingan_confirm_current_execution(...)` from the effective profile.
- Use `dispatch_context.confirm_post_delay` for the confirm dialog click post-delay in the manager dispatch closure.
- Add focused tests proving the preparation helper exposes the dispatch post-delay.
- Register the D-07 evidence and boundary in `FUNCTION_TREE.md`.

## Non-Goals

- No public CLI, task, catalog, API, or result schema changes.
- No change to confirm lookup, confirm click, result-dialog lookup, result-dialog close, artifact schemas, state paths, or audit schemas.
- No workflow builder, desktop primitive extraction, broker readiness claim, live acceptance claim, or production trading readiness claim.

## Modified Capability

- `tdx-desktop-trading-management`
