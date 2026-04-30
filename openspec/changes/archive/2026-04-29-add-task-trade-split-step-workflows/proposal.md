## Why

稳定桌面交易已经具备 `submit_ready(...)` 和 `confirm_current(...)` 两个分步 workflow，但日常可复用入口还停在 trade manager 和 `trade` CLI。只要 task/preset 层没有同步暴露，上层项目和固定操作流程就仍然要自己拼接这些边界步骤，稳定入口会继续分裂。

## What Changes

- Add stable task workflows for split-step desktop trading: `trade_submit_ready(...)` and `trade_confirm_current(...)`.
- Extend the `task` CLI group with `task trade-submit-ready` and `task trade-confirm-current`.
- Extend task preset execution so `task run --preset ...` can target the same split-step trade workflows with explicit CLI overrides preserved.
- Keep task result payloads aligned with the underlying stable trade manager results, including `trade_safety`, readiness summaries, and artifact visibility.

## Capabilities

### New Capabilities
- `tdx-task-trade-split-step`: Stable task-facing workflows for pre-confirm submit boundary and current-confirm advancement of desktop trades.

### Modified Capabilities
- `tdx-task-management`: Stable task management now includes split-step desktop trade workflows and allows preset-driven task execution to target them.

## Impact

- Affected code:
  - `tdxquant/api/task.py`
  - `tdxquant/cli.py`
  - `tdxquant/tasking.py`
  - `runtime/task-profiles.json`
  - `tests/test_api_manager.py`
  - `tests/test_api_cli.py`
- Affected docs:
  - task / function map / next-step documentation
