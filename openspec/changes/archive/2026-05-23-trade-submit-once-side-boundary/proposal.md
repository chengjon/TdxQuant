## Why

D-08 records Ping An submit-once as partial because buy submit-once is explicit, while sell submit-once is only a compatibility route through `side=sell + execution_mode=submit_once`. The CLI and task layers should expose that side boundary directly so readers and operators do not infer a hidden dedicated sell-submit-once implementation.

## What Changes

- Add an explicit `side` selector to stable submit-once CLI and task paths, defaulting to `buy`.
- Route `side=sell` through the existing Ping An sell execution chain while preserving the submit-once task/CLI entry boundary.
- Keep legacy `pingan-buy-submit-once` as buy-only compatibility.
- Update `FUNCTION_TREE.md` D-08 evidence and boundary without claiming full broker/exception coverage.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-desktop-trading-cli-entry`: submit-once CLI accepts an explicit buy/sell side selector.
- `tdx-task-management`: submit-once task accepts an explicit buy/sell side selector.

## Impact

- Affected code: `tdxquant/cli.py`, `tdxquant/api/task.py`.
- Affected tests: `tests/test_api_cli.py`, `tests/test_api_manager.py`.
- Documentation: `FUNCTION_TREE.md`.
- Dependencies: none.
