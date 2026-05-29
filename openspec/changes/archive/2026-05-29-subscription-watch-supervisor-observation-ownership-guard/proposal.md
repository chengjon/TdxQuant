## Why

Supervisor tick/run observations are now persisted into the active control statefile, but those writes should not attach stale observations to a different run if the active state changes between the control action and the best-effort observation merge. This slice hardens the statefile ownership boundary before adding any long-running supervisor daemon.

## What Changes

- Add an ownership guard for supervisor tick observation persistence when the tick result identifies an expected run.
- Add the same ownership guard for supervisor run observation persistence when the aggregate observation identifies an expected run.
- Preserve existing tick/run response envelopes and diagnostics projections.
- Preserve the boundary: no new daemon, scheduler, automatic retry, provider readiness proof, or lifecycle ownership claim.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-task-subscription-watch-background-control`: supervisor observation persistence becomes ownership-guarded when the expected run id is known.

## Impact

- Affected code: `tdxquant/subscription_watch_background.py`.
- Affected tests: `tests/test_subscription_watch_background.py`.
- Affected registry/specs: `FUNCTION_TREE.md`, background-control OpenSpec.
