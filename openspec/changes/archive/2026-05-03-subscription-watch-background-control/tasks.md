## 1. Worker-local background control contract

- [x] 1.1 Add stable background-control read models for `status`, `list`, and artifact discovery to `subscription_watch_background.py`
- [x] 1.2 Add stable diagnostic reads for `events` and `runner.log` tail views on canonical run artifacts
- [x] 1.3 Lock single-active replay, startup-timeout failure, noop stop, and stale-process reconciliation semantics with focused controller tests

## 2. Bridge alignment

- [x] 2.1 Refactor `bridge_http.py` to consume background-control read models instead of reconstructing worker-local state directly
- [x] 2.2 Preserve existing bridge transport envelope, auth checks, and endpoint shapes while delegating lifecycle/read semantics to background control

## 3. Docs and verification

- [x] 3.1 Update subscription-watch / bridge contract docs to reference the formal background-control capability
- [x] 3.2 Add or refresh bridge tests to lock active-only status, recent list views, and canonical artifact/log/event discovery
- [x] 3.3 Run targeted background-control and bridge verification plus `openspec validate subscription-watch-background-control --type change --strict`
