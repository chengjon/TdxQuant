## Design

The catalog parser currently shares one argument helper for `run`, `plan`, and `preview`. This change keeps the shared helper but adds an opt-in flag for plan/preview-only side arguments.

`catalog plan` and `catalog preview` will accept `--side buy|sell`. The existing preset merge behavior already gives command-line values precedence over preset options, so the resolved namespace and `trade_plan_boundary` can reflect the override without changing dispatch code.

`catalog run` will continue to omit `--side`, preserving the execution surface. Side-specific execution remains available through existing direct trade/task commands and registered side-specific entries.

## Boundaries

- This is a non-executing catalog plan/preview change.
- It must not execute submit-once, task, report, bundle, provider, buy/sell, submit-ready, or confirm-current workflows.
- It must not add `--side` to `catalog run`.
- It does not prove broker readiness, safety approval, production trading availability, or complete desktop exception coverage.

