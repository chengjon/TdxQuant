## Context

The catalog already contains:

- `task-buy-submit-once`, a task entry that sets `side=buy`.
- `buy-submit-once-pingan-exception-review`, `buy-submit-once-pingan-rejection-review`, and `buy-submit-once-pingan-failure-review`.
- Generic `submit-once-pingan-complete-review`, which still uses `task-submit-once`.

The missing piece is a side-explicit happy-path review bundle for buy submit-once.

## Design

Add a single runtime bundle:

- `buy-submit-once-pingan-complete-review`
- labels: `trading`, `submit`, `pingan`, `buy-submit-once`, `audit`, `success`, `followup`
- steps:
  - `trade` -> `task-buy-submit-once`
  - `success` -> `daily-success`
  - `audit` -> `audit-daily-pingan-confirmed`

Catalog planning should resolve all steps without dispatching execution. The existing generic submit-once bundles remain available for backward compatibility.

## Boundaries

- No new task, report, trade manager, gateway, or desktop execution primitive is added.
- The bundle only composes existing catalog entries.
- Real trade execution remains guarded by existing task arguments, profiles, broker environment, and safety constraints.
