## Context

The catalog already exposes:

- `task-buy`, backed by `task-buy-default`.
- `guarded-pingan-buy-complete-review`, backed by `guarded-buy`.
- PingAn confirmed audit report entries and daily success report entries.

The missing piece is a complete-review bundle for ordinary `task-buy`.

## Design

Add a single runtime bundle:

- `buy-pingan-complete-review`
- labels: `trading`, `buy`, `pingan`, `audit`, `success`, `followup`
- steps:
  - `trade` -> `task-buy`
  - `success` -> `daily-success`
  - `audit` -> `audit-daily-pingan-confirmed`

Catalog planning should resolve all steps without dispatching execution. Existing guarded-buy bundles remain available and unchanged.

## Boundaries

- No new trade manager, gateway, UI automation, or report primitive is added.
- The bundle only composes existing task and report catalog entries.
- Real buy execution remains subject to existing order arguments, profiles, broker environment, and safety constraints.
