## Why

桌面交易稳定入口已经有 `submission_key`、`max_price` 和 submission ledger，但日常使用更常走 `task trade-buy / trade-submit-once / guarded-trade-buy`。如果 task 层不能透传这些安全控制，上层调用者就仍然需要绕过 task 层，实际使用边界会再次分裂。

## What Changes

- Extend stable task-layer desktop trade workflows to accept and forward `submission_key` and `max_price`.
- Extend `task run --preset ...` so task preset execution can carry the same safety-control options with explicit CLI overrides preserved.
- Keep task-layer result payloads aligned with the underlying trade result so `trade_safety` and ledger artifacts remain visible through task workflows.

## Capabilities

### New Capabilities

### Modified Capabilities
- `tdx-task-management`: Stable trade-oriented task workflows now accept and forward desktop trade safety controls through direct task commands and preset-driven task execution.

## Impact

- Affected code:
  - `tdxquant/api/task.py`
  - `tdxquant/cli.py`
  - `tests/test_api_manager.py`
  - `tests/test_api_cli.py`
- Affected docs:
  - task / function map documentation
