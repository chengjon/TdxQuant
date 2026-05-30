## Why

D-07/D-08 still list retry policy as a remaining desktop lifecycle gate. Current PingAn `dialog_readiness` says retry policy remains incomplete, but it does not expose a stable read-only status describing whether retry/backoff is configured or executed.

## What Changes

- Add a read-only `retry_policy_status` payload to PingAn `desktop_lifecycle_gate_status`.
- Report the current policy as explicitly non-executing and not configured for supervised retry/backoff unless future profile fields provide otherwise.
- Preserve current behavior: no retry, no recovery, no resubmission, no backoff sleep, no ledger/state/audit writes.
- Register the evidence in `FUNCTION_TREE.md` while keeping D-07/D-08 `[部分实现]`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-desktop-trading-dialog-readiness`: expose read-only retry/backoff policy status in lifecycle readiness.
- `tdx-desktop-trading-safety`: register retry/backoff policy status as partial lifecycle evidence only.
- `tdx-function-tree-registry`: require D-07/D-08 to record the status without claiming implemented status.

## Impact

- `tdxquant/trade/manager.py`
- `tests/test_trade_manager.py`
- `FUNCTION_TREE.md`
- OpenSpec specs for dialog readiness, desktop trading safety, and FUNCTION_TREE registry
