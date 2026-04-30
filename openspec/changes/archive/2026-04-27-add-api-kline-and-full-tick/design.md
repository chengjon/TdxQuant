## Context

当前项目在 query manager 路径里已经存在两块未对齐现象：

- `TdxApiManager.market.kline(...)` 已有 Python 入口，但 `api` 二级 CLI 还没有 `kline` 子命令。
- `run_tdx_data_snapshot(...)` 实际调用的是 `tq.get_full_tick(...)`，但当前对外名字仍然是 `snapshot`，缺少显式 `full-tick` 语义入口。

这会带来两个问题：

- 标准 `api` CLI 与 Python manager 覆盖不一致。
- “市场快照”与“分笔 / full-tick”在命名上混在一起，不利于后续继续扩 query manager。

本次变更适合单独落一轮，因为它跨 `bridge.py`、`market.py`、`manager.py` 和 `cli.py`，但范围仍然足够小，可作为后续 `get_trading_dates`、`refresh_kline`、`download_file` 等能力包的模式样板。

## Goals / Non-Goals

**Goals:**

- 为 `api` 二级命令补齐 `kline` 标准入口。
- 为 `market` 域补齐显式 `full_tick` 入口。
- 保持现有 `api snapshot`、`tdx-data-kline`、`tdx-data-snapshot` 等已有路径兼容。
- 明确 manager / CLI 命名，使“market snapshot”与“full tick”不再继续混淆。

**Non-Goals:**

- 不改 `get_market_snapshot` 现有行为。
- 不重命名或删除既有 flat 命令。
- 不在本次一起引入 `get_trading_dates`、`refresh_kline`、`download_file`。
- 不在本次扩展订阅、告警、财务或交易数据面能力。

## Decisions

### 1. 为 full-tick 新增显式路径，而不是直接改写 `snapshot`

决策：

- 新增显式 `full_tick` 路径：
  - `bridge`: `run_tdx_full_tick(...)`
  - `market`: `MarketApi.full_tick(...)`
  - `manager`: `manager.market.full_tick(...)`
  - `cli`: `api full-tick`
- 保留现有 `snapshot` 路径不删除，继续作为兼容入口存在。

原因：

- 直接把 `snapshot` 改成真正的 `get_market_snapshot` 会改变既有行为，风险不必要。
- 当前已有 `market_snapshot` 明确对应官方快照接口；新增 `full_tick` 可以把语义补正，而不破坏历史脚本。

备选方案：

- 方案 A：直接把 `snapshot` 重定向到 `get_market_snapshot`
  - 放弃，原因是会破坏现有行为。
- 方案 B：维持现状，不新增显式 `full_tick`
  - 放弃，原因是语义长期混乱，后续能力矩阵也无法清晰归档。

### 2. `api kline` 直接复用现有 manager 参数模型

决策：

- 新增 `api kline` 子命令时，参数模型直接对齐现有 `tdx-data-kline` 和 `manager.market.kline(...)`：
  - `--code`
  - `--period`
  - `--start-time`
  - `--end-time`
  - `--count`
  - `--dividend-type`
  - `--field`
  - `--fill-data`

原因：

- 这能保持 `api` 和 flat 命令迁移成本最低。
- `manager.market.kline(...)` 已经定义了标准形状，本次只需要让 CLI 跟上，而不是重新设计一套入参。

备选方案：

- 方案 A：为 `api kline` 做更“简化”的参数集合
  - 放弃，原因是会让 Python manager、flat CLI、nested CLI 三套参数模型分叉。

### 3. 测试聚焦 parser、dispatch 与 manager 可见性

决策：

- parser 测试验证 `api kline` / `api full-tick` 的参数解析。
- CLI dispatch 测试验证新子命令走 `TdxApiManager`。
- manager 测试验证 `market.full_tick(...)` 暴露存在，并附带 manager metadata。

原因：

- 本次是“标准入口对齐”变更，风险主要在 parser / dispatch / manager surface，而不是底层算法。

## Risks / Trade-offs

- [命名继续双轨一段时间] → 通过新增显式 `full-tick`，先把语义纠正，再保留旧路径兼容。
- [CLI 参数继续膨胀] → 本次复用现有 `tdx-data-kline` 参数模型，避免再发明新方言。
- [用户仍可能混淆 `snapshot` 和 `market-snapshot`] → 文档与 spec 中明确：`full-tick` 是显式入口，后续优先推荐新入口。
- [测试覆盖主要在入口层] → 这是本轮有意取舍；底层 bridge 调用仍复用已有模式。
