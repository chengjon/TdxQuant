# PingAn Order Dispatch Runner Kwargs Design

## Context

`PingAnOrderDispatchOptions` already centralizes profile-derived desktop runner parameters. It exposes `base_kwargs(...)` for the HID submit probe path and `fast_kwargs(...)` for buy/sell fast paths. The manager still selects which helper to call at each order callsite.

The next D-08 increment should keep runner choice in the manager but move the kwargs shape choice behind a single internal method so callsites have a consistent dispatch-options API.

## Goals

- Introduce `runner_kwargs(..., fast_inputs: bool)` on `PingAnOrderDispatchOptions`.
- Make `runner_kwargs(fast_inputs=False, ...)` equivalent to `base_kwargs(...)`.
- Make `runner_kwargs(fast_inputs=True, ...)` equivalent to `fast_kwargs(...)`.
- Update buy/sell/submit-once callsites to use `runner_kwargs(...)`.

## Non-Goals

- Do not move desktop runner selection out of manager callsites.
- Do not change order execution request, idempotency, risk gate, handler bundle, result builder, finalize, or audit behavior.
- Do not change public manager, CLI, task, or catalog contracts.

## Compatibility

`base_kwargs(...)` and `fast_kwargs(...)` stay available. The new selector is an internal convenience method used by manager callsites.

## Validation

- Add a red test proving `runner_kwargs(...)` returns the existing base and fast kwargs shapes.
- Run focused PingAn trade execution/manager/gateway tests.
- Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
