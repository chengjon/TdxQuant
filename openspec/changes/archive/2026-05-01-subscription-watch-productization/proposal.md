## Why

`subscription-watch` 已经能在前台打开 runtime subscription session 并持续接收行情事件，但它此前更像一条“命令执行流程”，还没有被收口成稳定的 run artifact contract。现在查询 envelope、discovery payload 和 replay fixtures 都已经完成 hardening，订阅线需要跟进收口，避免上层仍然依赖终端输出或临时文件约定。

## What Changes

- 将 `subscription-watch` 固定为一次独立 `run`，每次执行生成新的 `run_id` 目录。
- 将 `events.jsonl` 升级为唯一 canonical 事件 contract，并为每个事件补齐稳定的 run 级元数据。
- 为每次运行固定 `manifest.json`、`status.json`、`summary.json` 三类 machine-readable artifacts。
- 保留 `events.csv` 及显式输出路径参数作为兼容投影，不再把它们视为正式 contract。
- 为 `subscription-watch` 补齐 representative replay fixtures、contract tests 和文档说明。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-task-subscription-watch`: 补充 run 目录、manifest/summary artifact、canonical JSONL 与兼容 CSV 的正式 contract。
- `tdx-provider-subscription-event-contract`: 扩展事件行必须包含的稳定 run 元数据与固定的 reconnect metadata 位置。
- `tdx-provider-replay-fixtures`: 补充 `subscription-watch` run artifact fixtures，并把它们纳入稳定内建 fixture catalog。

## Impact

- 受影响代码：`tdxquant/api/task.py`、`tdxquant/subscription_event.py`、新增 `tdxquant/subscription_watch_run.py`、`tdxquant/replay_fixtures.py`
- 受影响资产：`tdxquant/fixtures/provider/subscription-watch-*`、`subscription-event-batch.jsonl`
- 受影响测试：`tests/test_api_manager.py`、`tests/test_replay_fixtures.py`、`tests/test_subscription_event_contract.py`、新增 `tests/test_subscription_watch_run.py`
- 受影响文档：`docs/TdxQuant_Next_Steps.md` 以及订阅/fixture 相关说明
