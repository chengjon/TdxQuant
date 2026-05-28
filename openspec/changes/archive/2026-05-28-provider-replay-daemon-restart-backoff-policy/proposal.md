# Provider Replay Daemon Restart Backoff Policy

## Why

E-06 now has a foreground supervisor loop that observes one replay daemon child and refreshes lifecycle state. It still records child exit without recovery. A conservative, explicit restart/backoff policy is the next step before process ownership hardening and real provider lifecycle adapters.

## What Changes

- Extend the foreground supervisor with an opt-in `on-failure` restart policy.
- Keep the default policy as `never`.
- Add bounded restart controls: max restarts and fixed backoff seconds.
- Write `state=backoff` before sleeping for retry.
- Write `state=failed` when restart budget is exhausted.
- Add CLI flags on `provider-replay daemon supervise`.
- Add tests for successful retry, exhausted retry, and parser/dispatch propagation.
- Update `FUNCTION_TREE.md` E-06 evidence and boundary.

## Non-Goals

- No default automatic restart.
- No exponential backoff or jitter.
- No restart window persistence across separate supervisor runs.
- No port ownership inference.
- No process command-line ownership validation.
- No real provider or broker lifecycle management.
- No broker/workflow/write readiness claim.

