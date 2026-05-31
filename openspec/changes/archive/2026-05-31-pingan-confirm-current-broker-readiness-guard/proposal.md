## Why

D-07 now has owner-lock guard coverage and explicit exception popup handling for `confirm_current`, but the manual confirmation click path can still be entered without an opt-in broker runtime readiness check. `trade preflight` already performs readonly broker health checks; this change makes that broker readiness evidence available as an execution guard for `confirm_current` without changing default behavior.

This is a bounded safety guard, not a production readiness claim. It rejects before confirm dialog lookup/click only when the caller explicitly requires broker readiness.

## What Changes

- Add optional broker readiness guard parameters to `TdxTradeManager.pingan.confirm_current(...)`.
- Expose and forward `--require-broker-readiness` on stable `trade confirm-current` and `task trade-confirm-current`.
- Preserve current confirm-current behavior when the guard is omitted.
- Register the evidence in `FUNCTION_TREE.md` for D-07 while keeping the node `[部分实现]`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-desktop-trading-safety`: PingAn confirm-current shall honor an opt-in broker runtime readiness guard before dialog lookup/click.
- `tdx-api-cli-entry`: Stable confirm-current CLI entrypoints shall accept and forward the broker readiness guard option.
- `tdx-task-management`: Task confirm-current shall accept and forward the broker readiness guard option to the PingAn manager method.
- `tdx-function-tree-registry`: D-07 shall cite confirm-current broker readiness guard evidence while preserving partial status and explicit boundaries.

## Impact

- Affected code: `tdxquant/trade/manager.py`, `tdxquant/api/task.py`, `tdxquant/cli.py`.
- Affected tests: focused PingAn trade manager, task manager, CLI parser/dispatch, and FUNCTION_TREE registry tests.
- Runtime behavior remains opt-in. No lifecycle owner acquisition/release, process start/stop/restart/supervision, retry/backoff/recovery, live acceptance, or D-07 status promotion is introduced.
