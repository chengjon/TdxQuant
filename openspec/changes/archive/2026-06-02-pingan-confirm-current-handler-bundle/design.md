# PingAn Confirm-Current Handler Bundle Design

## Context

The order execution seam now accepts `PingAnOrderExecutionHandlers`, which makes the order callsite easier to audit and keeps result policy callbacks together. Confirm-current has a parallel internal seam but still receives `build_rejected_result`, `attach_metadata`, `attach_safety_metadata`, and `finalize_result` as separate keyword arguments.

The next D-07 increment should align confirm-current with that order pattern without moving desktop UI primitives or changing externally visible behavior.

## Goals

- Introduce `PingAnConfirmCurrentExecutionHandlers` as an internal dataclass in `tdxquant/trade/pingan_execution.py`.
- Preserve the existing confirm-current execution behavior for gate rejection, dispatch timing, metadata attachment, safety metadata attachment, and finalization.
- Keep `execute_pingan_confirm_current(...)` compatible with current callback keyword arguments so existing direct tests and downstream internal callers remain valid.
- Update the manager callsite to pass a single `handlers=` object after local metadata/safety closures are prepared.

## Non-Goals

- Do not move confirm lookup, confirm click, result-dialog lookup, or result-dialog close primitives out of the manager dispatch callback.
- Do not change public manager method parameters or result payload shapes.
- Do not introduce generic workflow infrastructure.

## Compatibility

`execute_pingan_confirm_current(...)` will accept either `handlers=` or the existing individual callback keyword arguments. If no handler bundle is provided, all legacy callback arguments remain required.

## Validation

- Add a red test that calls `execute_pingan_confirm_current(..., handlers=...)` and verifies the handler bundle path drives metadata, safety metadata, finalize, timing, and dispatch behavior.
- Run focused PingAn trade execution/manager/gateway tests.
- Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
