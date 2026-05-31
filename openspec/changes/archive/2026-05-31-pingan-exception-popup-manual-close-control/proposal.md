## Why

D-07/D-08 already record readonly exception popup detection through `trade dialog-readiness`, but the registered boundary still says exception popup handling is manual and unavailable. Operators can see that an exception-like result popup exists, but there is no stable PingAn manager/CLI control for explicitly closing that recognized popup without entering the broader order workflow.

This change closes one bounded desktop lifecycle gap by adding an operator-invoked exception popup inspect/close control. It remains partial evidence: it does not retry, recover, resubmit, manage processes, or prove broker readiness/live acceptance.

## What Changes

- Add a `TdxTradeManager.pingan.exception_popup(...)` control that can inspect the current result popup and, when explicitly confirmed, close a recognized exception-like popup.
- Add a stable `trade exception-popup` CLI entrypoint with `--action inspect|close` and `--confirm-close`.
- Keep inspect readonly and make close fail before clicking unless the operator supplies `--confirm-close`.
- Register the evidence in `FUNCTION_TREE.md` for D-07/D-08 while keeping both nodes `[部分实现]`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-desktop-trading-safety`: PingAn desktop trading shall expose an explicit exception popup inspect/close control that does not retry, recover, or submit orders.
- `tdx-api-cli-entry`: Stable trade CLI shall expose and dispatch the PingAn exception popup inspect/close control.
- `tdx-function-tree-registry`: D-07/D-08 shall cite exception popup manual close control evidence while preserving partial status and explicit boundaries.

## Impact

- Affected code: `tdxquant/trade/manager.py`, `tdxquant/cli.py`.
- Affected tests: focused PingAn trade manager, CLI parser/dispatch, and FUNCTION_TREE registry coverage.
- Runtime behavior is operator-invoked only. No task entry, catalog workflow execution, automatic recovery/retry/resubmission, process lifecycle ownership, broker readiness proof, or status promotion is introduced.
