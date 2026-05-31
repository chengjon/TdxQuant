## Why

Stable `trade buy/sell/submit-once` commands can now require local lifecycle owner-lock ownership before PingAn desktop automation, but the task-managed execution entrypoints still cannot opt into that same guard. This leaves `task trade-buy`, `task trade-sell`, and `task trade-submit-once` as inconsistent side-effecting entrypoints.

## What Changes

- Add optional lifecycle owner-lock requirement inputs to task trade workflows.
- Thread the inputs from `task trade-buy`, `task trade-sell`, and `task trade-submit-once` CLI commands into `TdxTaskManager`.
- Forward the guard options from `TdxTaskManager.trade_buy`, `trade_sell`, and `trade_submit_once` into the existing PingAn manager execution methods.
- Register the task-level owner-lock execution guard as partial D-07/D-08 evidence only.
- Keep default behavior unchanged: the guard remains inactive unless explicitly requested.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-task-management`: task trade workflows can forward the opt-in lifecycle owner-lock execution guard.
- `tdx-api-cli-entry`: stable task trade commands accept lifecycle owner-lock requirement arguments.
- `tdx-function-tree-registry`: D-07/D-08 register task-level execution owner-lock guard coverage without status promotion.

## Impact

- Code: `tdxquant/api/task.py`, `tdxquant/cli.py`, `FUNCTION_TREE.md`.
- Tests: focused task manager/CLI and FUNCTION_TREE registry tests.
- No process lifecycle control, lock acquisition/release, broker readiness, live/manual acceptance, or workflow builder behavior is introduced.
