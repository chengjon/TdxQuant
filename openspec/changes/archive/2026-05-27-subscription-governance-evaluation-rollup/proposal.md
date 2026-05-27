## Why

HTTP and CLI `watch-status --view summary` already expose detailed advisory governance metadata, including `evaluation_summary`. Callers that only need the evaluation posture still have to read several count and primary-component fields and infer stale/fresh/not-evaluated state themselves.

## What Changes

- Add an additive read-only `governance.evaluation_rollup` object to HTTP and CLI watch-status summary views.
- Derive the object only from existing `governance.evaluation_summary` and sibling `staleness_evaluated` metadata.
- Keep the rollup advisory and non-executable: it must not trigger reconnect, backoff, restart, lifecycle control, HTTP behavior, SSE behavior, or event-stream behavior.

## Impact

- Affected spec: `tdx-subscription-long-run-status-summary`
- Affected code: HTTP summary projection, CLI summary projection, focused tests, and `FUNCTION_TREE.md` B-16/E-09 registry evidence/boundary.
