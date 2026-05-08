## 1. Worker bridge projection and auth regression

- [x] 1.1 Lock `watch/status` as a verbatim projection of controller `status()` for `running / reconnecting / degraded / stale_process_state`
- [x] 1.2 Keep `Authorization` and `master_allowlist` failures transport-scoped and verify they reject before controller reads
- [x] 1.3 Ensure `health` and active-run fallback use control-only reads instead of depending on parseable `status.json`

## 2. Master-side registry/client transport normalization

- [x] 2.1 Preserve bridge JSON HTTP error bodies exactly as returned by workers
- [x] 2.2 Normalize invalid UTF-8 success bodies, invalid JSON success bodies, non-object JSON payloads, and `connection refused` into stable transport failures
- [x] 2.3 Lock direct registry helper coverage for `health`, `watch-list`, `watch-artifacts`, `watch-events`, and `watch-logs`

## 3. CLI remote-control pass-through contract

- [x] 3.1 Add or lock parser/dispatch coverage for `bridge health`, `bridge watch-list`, `bridge watch-artifacts`, `bridge watch-events --tail`, and `bridge watch-logs --tail`
- [x] 3.2 Keep CLI stdout as direct registry/client JSON pass-through and preserve JSON failure output for bridge/client errors
- [x] 3.3 Verify `bridge watch-status` remains an active-snapshot reader rather than a historical `run_id` lookup interface

## 4. Docs, validation, and archive

- [x] 4.1 Update subscription-watch bridge/control-plane docs to distinguish `control.state` from `watch_status.state` and document the remote-control read contract
- [x] 4.2 Run focused bridge/background/CLI regression coverage
- [x] 4.3 Validate the OpenSpec change and archive it after syncing the stabilized contract into main specs
