## Why

Subscription long-run summary views already expose bounded governance reason/action samples plus separate count, limit, hidden-count, and truncated flags. Consumers that only need to know whether the visible samples are complete must currently read several sibling fields and compare them.

Adding a compact `governance.sample_summary` keeps the B-16/E-09 status registry explicit while preserving the existing safe projection boundary: it summarizes sample metadata only, omits full advisory reasons/actions, and does not alter reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

## What Changes

- Add `governance.sample_summary` to HTTP and CLI `bridge watch-status --view summary` payloads.
- Derive the object only from already-computed reason/action sample metadata:
  - total counts
  - visible sample counts
  - hidden sample counts
  - sample limits
  - truncated flags
- Preserve existing top-level governance sample fields for compatibility.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.

## Impact

- Affected code: `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-subscription-long-run-status-summary`
- Verification: focused pytest for bridge/API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
