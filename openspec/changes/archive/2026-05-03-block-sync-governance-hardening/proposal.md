## Why

`block` 域已经具备第一版写治理设计和 `block_mutation` 治理入口，但 bridge 侧还没有完整切换到“写前治理 + 延迟执行回调”模式，因此它仍然只是“部分可治理的单次写操作”，还不是“可重复执行、可预测”的同步能力。当前上层如果想把标准化 watchlist 推到 TongDaXin 自定义板块，仍需要自己处理：

- 覆盖写与增量写语义
- 目标板块不存在时的稳定决策
- dry-run / plan-only 预演
- `mutation_key` 在同步请求层面的幂等和冲突
- 变更 diff 的 machine-readable 结果

因此，需要一边补齐 bridge 五条 block 写路径对当前治理入口的实际接入，一边在现有 `block_mutation` 治理基础上新增一条明确的 `block sync` capability，把 `watchlist -> TongDaXin block` 收成正式 provider-ready contract。

## What Changes

- 新增 `tdx-provider-block-sync` capability，第一版只覆盖单向 `watchlist -> TongDaXin block` 同步。
- 为 `block sync` 固定 `replace` / `merge` 两种写入语义，默认 `replace`。
- 为 `block sync` 固定 `create_if_missing` 与 `dry_run` 语义。
- 为 `block sync` 固定同步视角结果摘要：`added_symbols`、`removed_symbols`、`unchanged_symbols`、`desired_symbols`、`observed_symbols`、`created_block`、`would_create_block`、`governance_decision`、`governance_reason`。
- 明确 `show` 作为 sync 的执行选项存在，默认 `true`，但不参与目标状态比较。
- 保持底层真实写入继续复用现有 `block_mutation` 治理链和审计 artifact，而不是重新发明写安全逻辑。
- 显式补齐 bridge 五条 block 写路径到 `apply_block_mutation_safety(...)` 当前签名的接入，而不是继续假设前置 change 已完整落地。
- 为 manager / CLI / replay fixtures 补齐 block sync 入口与 representative samples。

## Capabilities

### New Capabilities

- `tdx-provider-block-sync`: 受治理的单向 watchlist/block 同步 contract。

### Modified Capabilities

- `tdx-provider-block-mutation-safety`: 明确 higher-level block sync workflow 可复用底层治理与审计 contract。
- `tdx-provider-replay-fixtures`: 为 block sync 补充 representative fixture samples。
- `tdx-api-management`: 暴露 manager 级 `block sync` 入口。
- `tdx-api-cli-entry`: 暴露 nested `api` 和 flat CLI 的 block sync 入口。

## Impact

- 受影响代码：
  - `tdxquant/api/manager.py`
  - `tdxquant/api/bridge.py`
  - `tdxquant/block_mutation.py`
  - 可能新增 `tdxquant/block_sync.py` 一类 orchestration 模块
  - 新增 block sync orchestration 模块与相关 CLI 分发
- 受影响测试：
  - block sync bridge / manager / CLI 合约测试
  - replay fixture / dry-run / create-if-missing / mutation-key 覆盖
- 受影响 fixtures：
  - 新增 block sync representative JSON fixtures
- 受影响文档与 spec：
  - block sync contract
  - block mutation safety
  - provider replay fixtures
  - Function Map / Next Steps 中的 block sync 规划口径
