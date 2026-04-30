## Context

当前 query manager 主线里已经把查询能力分成了 `market`、`meta`、`formula`、`block` 四个域，并通过嵌套 `api` CLI 暴露稳定入口。但官方接口文档里还有三类公共能力没有合适归属：

- `refresh_kline(stock_list, period)`
- `get_trading_dates(market, start_time, end_time, count)`
- `download_file(stock_code, down_time, down_type)`

这三类能力有两个共同特征：

- 它们不是纯行情读取，也不是纯元数据读取。
- 其中至少两类带有明显运行时副作用或运行时前置条件，例如本地缓存刷新、客户端下载文件。

如果把它们继续塞进 `market` 或 `meta`，会继续扩大域边界漂移；如果继续只保留零散 bridge 命令，又无法满足“manager 层统一日常使用”的目标。

## Goals / Non-Goals

**Goals:**

- 为 query API 增加 `runtime` 子域，承载公共运行时查询动作。
- 为 CLI 增加 `api trading-dates`、`api refresh-kline`、`api download-file` 三个嵌套入口。
- 为 flat bridge 层补齐对应命令，保持 bridge / manager 双入口结构一致。
- 保留现有 `refresh_cache` 顶层 manager 动作，不改变其既有行为和调用方。
- 为新入口补充 parser、dispatch、manager metadata、bridge delegation 测试。

**Non-Goals:**

- 不在本次把 `refresh_cache` 重命名或迁移进 `runtime` 子域。
- 不在本次处理订阅/告警、财务/交易数据面或 block 生命周期缺口。
- 不在本次增加下载后文件搬运、二次解析或额外状态落盘流程。
- 不触碰桌面自动化交易路径、task/report/catalog 场景层。

## Decisions

### 1. 用独立 `runtime` 子域承载公共运行时能力

决策：

- 新增 `tdxquant/api/runtime.py`
- 新增 `TdxApiManager.runtime`
- `runtime` 子域只承载：
  - `trading_dates(...)`
  - `refresh_kline(...)`
  - `download_file(...)`

原因：

- `refresh_kline` 和 `download_file` 都带有运行时副作用，不适合继续膨胀 `market` 的只读职责。
- `get_trading_dates` 虽然是查询，但它更像公共运行时工具能力，和单只证券或板块域也不强绑定。
- 这能把“公共运行时能力”和“领域查询能力”边界显式区分开，后续继续补 runtime / output / path 治理也更顺手。

备选方案：

- 方案 A：把三者都塞进 `market`
  - 放弃，原因是会让 `market` 继续混入缓存治理和文件下载副作用。
- 方案 B：保持只有 flat bridge 命令，不引入 manager 子域
  - 放弃，原因是不符合当前“manager 层统一日常入口”的总方向。

### 2. 嵌套 `api` 用业务友好命名，flat bridge 贴近底层动作

决策：

- 嵌套 `api` 子命令：
  - `api trading-dates`
  - `api refresh-kline`
  - `api download-file`
- flat bridge 命令：
  - `tdx-get-trading-dates`
  - `tdx-refresh-kline`
  - `tdx-download-file`

原因：

- 嵌套 `api` 面向日常管理层，命名应和现有 `stock-list`、`sector-list` 风格一致。
- flat bridge 更接近官方函数名和桥接层动作，保留 `get_` 前缀可降低对照文档时的认知成本。

### 3. `refresh_kline` 不复用现有 `refresh_cache`

决策：

- `refresh_kline(stock_list, period)` 新增独立 bridge 包装和 manager 入口。
- 现有 `refresh_cache(market, force)` 完全保留，继续作为顶层治理动作。

原因：

- 官方文档中的 `refresh_kline` 是按证券列表与周期定向刷新历史数据。
- 当前 `refresh_cache` 是按市场与 force 进行更通用的缓存治理。
- 两者入参和语义都不同，强行复用会让调用方拿到错误抽象。

### 4. 下载文件只暴露官方运行时结果，不追加生产路径副作用

决策：

- `download_file(...)` 直接返回 TdxQuant 运行时原始结果。
- 结果中补充固定提示：官方客户端下载文件位于 Windows 侧 `.\PYPlugins\data`。

原因：

- 这次变更的重点是“把能力纳入 manager 和 CLI 标准入口”，不是构建文件搬运流水线。
- 先把入口和结构稳定下来，后续如果需要做下载目录收口、任务编排或产物二次解析，再单独开变更。

## Risks / Trade-offs

- [active spec 与 archive delta 暂时不同步] → 本次先继续实现与校正主线能力，最后统一做 spec 同步和归档。
- [runtime 域增加一个新分层] → 这是有意增加，用来避免把 `market/meta` 再堆胖。
- [download_file 仍然依赖 Windows 客户端本地路径] → 本次通过结构化提示暴露该前提，不在本轮做路径搬运。
- [bridge flat 命令继续增加] → 这是当前项目明确保留的双入口策略，后续由 `catalog/task/report` 收口高频入口。
