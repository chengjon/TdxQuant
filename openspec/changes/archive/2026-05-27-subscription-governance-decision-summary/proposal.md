# subscription governance decision summary

## Why

Bridge watch-status summary views already expose advisory governance fields such as `decision`, `requires_manual_review`, `staleness_evaluated`, `reason_count`, `action_count`, `reason_summary`, and `action_summary`. Consumers that only need compact decision posture currently have to reconstruct it from several siblings.

Adding `governance.decision_summary` keeps B-16/E-09 evidence compact while preserving the long-run governance boundary: it summarizes already-projected advisory metadata only and does not trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

## What Changes

- Add read-only `governance.decision_summary` to HTTP and CLI `watch-status --view summary`.
- Derive the object from existing governance summary sibling fields:
  - decision and manual-review flag
  - staleness-evaluated flag
  - reason/action counts
  - primary reason source and primary action severity when available
- Preserve existing sibling fields for compatibility.
- Update focused HTTP/CLI tests, OpenSpec, and `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.

## Impact

- Affected code: `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-subscription-long-run-status-summary`
- Verification: focused pytest for bridge HTTP/API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
