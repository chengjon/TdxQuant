# TdxQuant Provider Replay Fixtures

本文定义 TdxQuant 当前内置的 provider replay fixture bundle。

它的目标不是模拟 live runtime，而是提供一组稳定、仓内自带、可直接被上层项目消费的 contract fixtures，用于：

- contract test
- 离线联调
- replay 样例
- fake provider 输入资产

## 1. Current Scope

当前 fixture bundle 覆盖这些高价值 provider contract：

- 通用同步 provider result success / failure
- `formula.screen`
- `runtime.capabilities`
- `runtime.doctor`
- `block.send_user_block` 的 mutation safety 结果
- provider-level subscription event rows

支持两种格式：

- `json`
- `jsonl`

## 2. Stable Location

当前内置 fixture 位于：

- `tdxquant/fixtures/provider/`

推荐通过 loader helper 使用，而不是在上层项目里硬编码目录结构。

## 3. Loader Helpers

当前稳定 helper 位于：

- `tdxquant.replay_fixtures`

可用函数：

- `list_provider_replay_fixtures()`
- `get_provider_replay_fixture_path(name)`
- `load_provider_replay_fixture(name)`

其中：

- `list_provider_replay_fixtures()` 返回 fixture manifest
- `get_provider_replay_fixture_path(name)` 返回绝对路径
- `load_provider_replay_fixture(name)` 自动按 `json` 或 `jsonl` 解析

## 4. Current Fixture Names

当前第一版固定这些名字：

- `provider-result-success`
- `provider-result-failure`
- `formula-screen-success`
- `runtime-capabilities-success`
- `runtime-doctor-degraded`
- `block-send-user-block-applied`
- `subscription-event-batch`

这些名字应被视为对上层稳定的 sample 标识。

## 5. Python Example

```python
from tdxquant import list_provider_replay_fixtures, load_provider_replay_fixture

fixtures = list_provider_replay_fixtures()
formula_payload = load_provider_replay_fixture("formula-screen-success")
event_rows = load_provider_replay_fixture("subscription-event-batch")
```

其中：

- `formula_payload` 是一个 provider-facing JSON dict
- `event_rows` 是按源顺序解析后的 `list[dict]`

## 6. Current Boundary

这包当前已经解决：

- 内置 fixture 资产
- 稳定 fixture 名称
- 统一 loader
- JSON / JSONL contract test 基座

这包当前还没有解决：

- live runtime 自动 replay mode
- HTTP replay 服务
- daemon fake provider
- start / stop / status 形态的测试控制面

这些属于后续更高一层的 fake provider / integration hardening 工作。
