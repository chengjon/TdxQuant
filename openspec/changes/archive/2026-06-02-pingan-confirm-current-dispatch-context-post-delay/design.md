# PingAn Confirm-Current Dispatch Context Post Delay Design

## Context

`PingAnConfirmCurrentDispatchContext` currently carries the confirm-current dispatch options used by result builders and manager dispatch: result close behavior, lookup mode, confirm timeout, result timeout, and result close pre-delay. The actual confirm click post-delay remains a direct `effective_profile["confirm_post_delay"]` lookup in the dispatch closure.

The order side already has a dispatch options object that centralizes profile-derived runner kwargs. Confirm-current should get the same locality for its remaining post-click timing input, but the UI lookup/click code should stay in the manager callsite for now.

## Goals

- Add `confirm_post_delay` to the confirm-current dispatch context.
- Keep `_prepare_pingan_confirm_current_execution(...)` responsible for resolving the profile-derived value.
- Route the confirm click call through `dispatch_context.confirm_post_delay`.
- Preserve all existing public parameters, result shapes, metadata, safety metadata, and audit behavior.

## Non-Goals

- Do not move UI lookup/click code out of the manager dispatch callback.
- Do not add new desktop primitives.
- Do not change public manager, CLI, task, or catalog contracts.

## Compatibility

The context field is internal. Existing direct tests that construct `PingAnConfirmCurrentDispatchContext` should remain source-compatible by using a default `confirm_post_delay` value when the field is omitted.

## Validation

- Add a red test asserting `_prepare_pingan_confirm_current_execution(...)` exposes `dispatch_context.confirm_post_delay` from the effective profile.
- Run focused PingAn trade execution/manager/gateway tests.
- Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
