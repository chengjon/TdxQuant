## Why

`guarded-trade-buy` is a side-effecting PingAn task workflow that eventually delegates to `trade_buy`, but it cannot yet opt into the local lifecycle owner-lock execution guard. This leaves the guarded workflow less consistent than direct task trade entrypoints.

## What Changes

- Add optional lifecycle owner-lock guard inputs to `TdxTaskManager.guarded_trade_buy`.
- Add the same guard arguments to the `task guarded-trade-buy` CLI command.
- Forward guard options from guarded workflow dispatch into the delegated `trade_buy` call.
- Register the coverage in `FUNCTION_TREE.md` as partial D-07 evidence only.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-task-management`: guarded PingAn trade-buy workflow can forward owner-lock execution guard options.
- `tdx-api-cli-entry`: `task guarded-trade-buy` accepts lifecycle owner-lock guard arguments.
- `tdx-function-tree-registry`: D-07 registers guarded workflow owner-lock guard forwarding without status promotion.

## Impact

- Code: `tdxquant/api/task.py`, `tdxquant/cli.py`, `FUNCTION_TREE.md`.
- Tests: guarded task manager/CLI and FUNCTION_TREE registry tests.
- No default behavior change; no lifecycle control, lock acquisition/release, broker readiness, or live/manual acceptance is introduced.
