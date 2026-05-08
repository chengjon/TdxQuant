## Why

当前 `block` 写操作已经有 mutation summary、audit artifact 和可选 `mutation_key`，但仍然缺少真正的写治理：系统不会先读真实板块状态，也不会在“目标状态已达成”或“当前状态与请求冲突”时做稳定决策。这样 `block` 还不适合作为 watchlist/block 同步能力的正式基础。

## What Changes

- 为全部 5 条 `block` 写路径引入统一治理决策：`applied / noop / rejected / failed`。
- 在写前读取真实板块状态，并据此决定 `execute / skip / reject`，不再只做事后审计包装。
- 为 `mutation_key` 增加本地幂等与冲突检测：同 key 同请求可短路，同 key 不同请求稳定拒绝。
- 扩展 `block_mutation` 和 audit artifact，补齐 `governance_decision`、`governance_reason`、`desired_state`、`observed_state`。
- 为 `block` provider fixture 增加 `noop` / `rejected` representative samples，并用测试锁住 contract。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-provider-block-mutation-safety`: 从“写后审计”升级为“状态感知治理 + 幂等保护 + 稳定决策 contract”。
- `tdx-provider-replay-fixtures`: 为 block mutation 补充 `noop` / `rejected` 治理样例，并把治理字段纳入稳定 fixture contract。

## Impact

- 受影响代码：`tdxquant/block_mutation.py`、`tdxquant/api/bridge.py`
- 受影响测试：`tests/test_tdx_api_bridge.py`、`tests/test_api_manager.py`、`tests/test_api_cli.py`
- 受影响 fixtures：`tdxquant/fixtures/provider/block-send-user-block-applied.json`，以及新增 block mutation `noop` / `rejected` 样例
- 受影响文档与 spec：block mutation safety、provider replay fixtures、路线图和功能地图中的 block 治理表述
