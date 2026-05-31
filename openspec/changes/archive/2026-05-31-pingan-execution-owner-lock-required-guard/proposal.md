## Why

PingAn preflight can now require a local lifecycle owner lock, but side-effecting PingAn trade entrypoints still cannot opt into the same guard before desktop execution. This leaves the readiness gate advisory unless operators remember to run preflight separately.

## What Changes

- Add optional lifecycle owner-lock requirement inputs to PingAn buy/sell/buy-submit-once/sell-submit-once manager methods.
- Block desktop execution when the opt-in requirement is enabled and the local owner lock is missing, stale, released, unknown, or held by another token.
- Thread the guard through `PingAnDesktopTraderGateway` and stable `trade buy`, `trade sell`, and `trade submit-once` CLI commands.
- Record the guard failure as trade-safety/audit rejection evidence while not acquiring/releasing locks or controlling processes.
- Keep D-07/D-08 as `[部分实现]`.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-desktop-trading-safety`: side-effecting PingAn trade entrypoints can require local owner-lock ownership before desktop execution.
- `tdx-desktop-trading-cli-entry`: stable trade execution CLI commands accept lifecycle owner-lock requirement arguments.
- `tdx-securities-trader-gateway`: PingAn desktop gateway forwards owner-lock requirement options to manager execution methods.
- `tdx-function-tree-registry`: D-07/D-08 register the execution owner-lock guard as partial evidence only.

## Impact

- Code: `tdxquant/trade/manager.py`, `tdxquant/trader/adapters/pingan_desktop.py`, `tdxquant/cli.py`.
- Tests: focused manager, gateway/CLI, and FUNCTION_TREE registry tests.
- No default behavior change: the guard is inactive unless explicitly requested.
