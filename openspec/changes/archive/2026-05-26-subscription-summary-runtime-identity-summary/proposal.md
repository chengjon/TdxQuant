# subscription summary runtime identity summary

## Why

Bridge watch-status summary views already expose runtime identity sibling fields such as `control_state`, `watch_state`, `state_match`, `run_id_source`, `run_id_match`, and `pid_source`. Consumers that only need compact identity provenance currently have to reconstruct it from several siblings.

Adding `runtime.identity_summary` keeps B-16/E-09 evidence compact while preserving the long-run governance boundary: it summarizes already-projected identity metadata only and does not check PID liveness, prove run ownership, trigger reconnect/backoff/restart, or manage lifecycle.

## What Changes

- Add read-only `runtime.identity_summary` to HTTP and CLI `watch-status --view summary`.
- Derive the object from existing runtime summary sibling fields:
  - control/watch state and state match
  - run ID presence/source/match
  - PID presence/source
- Preserve existing sibling fields for compatibility.
- Update focused HTTP/CLI tests, OpenSpec, and `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.

## Impact

- Affected code: `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-subscription-long-run-status-summary`
- Verification: focused pytest for bridge HTTP/API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
