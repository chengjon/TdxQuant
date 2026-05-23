## Context

The catalog already has:

- `task-confirm-current`
- `confirm-pingan-complete-review`
- `confirm-current-pingan-exception-review`
- PingAn confirm-current rejected/failed/exceptions report entries

The missing piece is a `confirm-current-pingan-complete-review` alias that mirrors the existing complete-review workflow while using the more explicit `confirm-current` naming convention.

## Design

Add a single runtime bundle:

- `confirm-current-pingan-complete-review`
- labels: `trading`, `confirm`, `confirm-current`, `pingan`, `audit`, `success`, `followup`
- steps:
  - `confirm` -> `task-confirm-current`
  - `success` -> `daily-success`
  - `audit` -> `audit-daily-pingan-confirmed`

Catalog planning should resolve the bundle without dispatching execution. The older `confirm-pingan-complete-review` bundle remains available.

## Boundaries

- No change to `TdxTradeManager`, gateway, UI automation, or report semantics.
- No new confirm-current execution primitive is introduced.
- Real execution remains subject to existing task safety and broker environment requirements.
