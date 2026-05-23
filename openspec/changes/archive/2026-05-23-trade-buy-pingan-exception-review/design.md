## Context

The catalog already exposes:

- `task-buy`
- `buy-pingan-complete-review`
- `guarded-pingan-buy-exception-review`
- `guarded-pingan-buy-rejection-review`
- `guarded-pingan-buy-failure-review`
- ordinary PingAn buy audit report entries for exceptions, rejected, and failed states

The missing piece is the ordinary buy equivalent of the guarded-buy exception/rejection/failure trio.

## Design

Add three runtime bundles:

- `buy-pingan-exception-review`
- `buy-pingan-rejection-review`
- `buy-pingan-failure-review`

Each bundle will use:

- `trade` -> `task-buy`
- `audit` -> the corresponding existing PingAn buy audit report entry

These bundles are catalog aliases only. They do not change the buy task itself, the gateway, or desktop automation semantics.

## Boundaries

- No new trade manager primitive is added.
- Existing guarded-buy bundles remain available and unchanged.
- Real execution still requires the current trade arguments, profiles, and safety constraints.
