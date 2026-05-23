# Design

## Context

The full subscription watch status summary contains:

- `governance.decision`
- `governance.requires_manual_review`
- `governance.staleness_evaluated`
- `governance.actions`
- `governance.action_summary`

The reduced summary views intentionally omit verbose `actions`, but they should still expose whether stale thresholds were evaluated. This is a compact boolean and does not reveal extra operational details.

## Approach

Extend the governance projection allowlist in both summary-view builders from:

`decision`, `requires_manual_review`, `action_summary`

to:

`decision`, `requires_manual_review`, `staleness_evaluated`, `action_summary`

No data is recomputed. The value is copied only when present in the existing governance payload.

## Boundaries

- Summary views remain opt-in projections.
- `actions` remain omitted from the reduced view.
- Reconnect/backoff/restart behavior remains unchanged.
