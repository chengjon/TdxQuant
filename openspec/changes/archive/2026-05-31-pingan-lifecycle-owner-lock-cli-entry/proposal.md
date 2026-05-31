## Why

PingAn lifecycle owner lock behavior now exists at the manager layer, but operators cannot invoke it through the stable trade CLI. Adding an explicit CLI entry keeps the owner-lock gate discoverable without mixing it into order execution or workflow builders.

## What Changes

- Add a stable `trade lifecycle-owner-lock` CLI subcommand.
- Require explicit `--statefile-path` and `--owner-token`, and accept `--action status/acquire/release`, `--stale-after-seconds`, and `--force-stale`.
- Dispatch the CLI entry to `TdxTradeManager.pingan.lifecycle_owner_lock(...)`.
- Keep the CLI boundary local and non-trading: no order submission, no process start/stop/restart/kill/supervisor/backoff, and no catalog workflow execution.
- Register the CLI evidence in `FUNCTION_TREE.md` while keeping D-07/D-08 `[部分实现]`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-desktop-trading-cli-entry`: adds the explicit PingAn lifecycle owner lock CLI entry.
- `tdx-desktop-trading-safety`: records that the CLI entry remains statefile-only and cannot satisfy live trading gates by itself.
- `tdx-function-tree-registry`: requires D-07/D-08 to cite the CLI entry without status promotion.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`
- Affected registry: `FUNCTION_TREE.md`
