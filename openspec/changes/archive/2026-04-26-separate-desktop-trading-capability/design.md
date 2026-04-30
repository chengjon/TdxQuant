## Context

项目当前已经形成两个不同风险级别、不同运行形态的能力簇：

1. 查询 API 能力
   - 以 `tdxquant/api/bridge.py` 为底层桥接。
   - 已完成 `TdxApiManager`、`market.py`、`meta.py` 和 `api` 二级命令的 MVP 收敛。
   - 适合作为只读、低风险、稳定调用的统一管理面。

2. 桌面自动化交易能力
   - 以 `tdxquant/desktop/`、`tdxquant/brokers/`、`tdxquant/uia_inspector.py` 和交易 CLI 命令为主。
   - 真实联调已经沉淀出 Win32/UIA/HID 混合闭环，覆盖下单、确认推进、结果窗关闭、合同号提取与回填。
   - 具有明确的高风险和环境依赖属性，不能与只读查询管理层混为一谈。

API 管理 MVP 已经明确“不把桌面自动化路径并入 manager”。下一步正确方向不是继续把交易逻辑散放在 CLI 里，而是正式把它定义成一条与 API 管理层并列的 capability。

## Goals / Non-Goals

**Goals**

- 给桌面自动化交易定义正式 capability 名称、职责边界和未来顶层入口。
- 明确其与 `tdx-api-management` 的关系：并列、协同、共享规范，但不共用 manager。
- 为后续 `TradeManager`、`trade` CLI、task 编排层和稳定文档落点提供结构基础。
- 保证现有 `pingan-buy-submit-once`、`pingan-buy`、相关诊断命令和稳定流程继续可用。

**Non-Goals**

- 本次不重构现有交易执行代码。
- 本次不把交易命令迁移到新的 CLI 组。
- 本次不新增卖出、撤单、持仓或回报查询实现。
- 本次不把桌面交易能力改造成纯后台 API 或并入 `TdxApiManager`。

## Decisions

### 1. 桌面自动化交易单独建模为 capability

新增 `tdx-desktop-trading-management` 作为正式 capability，用于描述桌面自动化交易的统一治理范围。其覆盖：

- 运行时前置检查
- 窗口发现与窗口状态判断
- Win32 / UIA / HID 混合探测与输入
- 交易确认推进与结果窗处理
- 合同号、状态文件、日志回填

这样做的目的不是立即大改代码，而是先在规格层明确“这不是一组临时命令，而是一条正式能力线”。

### 2. 桌面交易与查询 API 并列，而不是下沉到同一 manager

查询 API 的特征是：

- 只读
- 参数规则稳定
- 可通过 profile 做日常标准化
- 适合统一落到 `TdxApiManager`

桌面交易的特征是：

- 高风险
- 强环境耦合
- 依赖前台窗口、焦点、弹窗状态和外部硬件
- 常常需要诊断分支、实验开关和实机验证

因此两者应采用“并列 capability，分别治理”的结构：

- `TdxApiManager` 负责查询能力
- 后续 `TradeManager` 负责桌面交易能力

二者可以在未来 task 层被共同编排，但不应共用一个 manager。

### 3. 桌面交易 CLI 应收敛到独立的 `trade` 命令组

当前交易侧主要通过扁平命令存在，例如：

- `pingan-buy-submit-once`
- `pingan-buy`
- `pingan-probe`
- `pingan-hid-submit-probe`
- 相关 `win32-*` / `uia-*` 诊断命令

后续不应把这些命令继续塞进 `api` 组，而应规划独立的 `trade` 二级入口，例如：

- `tdxquant trade buy`
- `tdxquant trade submit-once`
- `tdxquant trade probe`
- `tdxquant trade inspect`

但本次只定义 capability 和兼容规则，不直接迁移现有命令。

### 4. 桌面交易 capability 继续沿用“底层工具 + 业务适配 + 顶层管理”的分层

推荐的长期分层如下：

- 底层工具层：`desktop/win32.py`、`desktop/uia.py`、HID 工具、低层读写/点击/窗口操作
- 券商适配层：`brokers/pingan.py` 等特定客户端适配器
- 顶层交易管理层：未来的 `TradeManager`，负责 profile、耗时、日志、状态回填、结果标准化
- CLI / task 层：日常命令和场景化流程编排

这使桌面交易 capability 在结构上与 `tdx-api-management` 平行对应：

- API 侧：`bridge -> domain -> manager -> api CLI`
- Trade 侧：`desktop tools -> broker adapter -> trade manager -> trade CLI`

### 5. Task 层可以同时编排 API 和 Trade，但不改变底层 capability 归属

未来高频流程很可能同时需要：

- 先调用查询 API 做行情/标的/参数判断
- 再调用桌面交易能力执行买入
- 最后落日志、状态和结果文件

这属于 task 层职责，而不是把查询与交易强行并入一个 manager。也就是说：

- capability 归属保持独立
- 场景编排在更高层完成

## Risks / Trade-offs

- [短期内会存在“新规划，旧入口”并存] → 这是有意的低风险策略，先立 capability，再逐步收敛实现。
- [桌面交易结构仍有历史命令分散] → 本次通过规格明确未来落点，避免后续继续无序扩张。
- [若强行并入 API manager，会污染只读查询体系] → 因此必须保持并列关系。
- [trade CLI 未来迁移需要兼容大量现有命令] → 需要在后续 change 中明确兼容期和映射策略。
- [桌面交易的实验开关和实机差异较多] → 顶层交易 manager 必须接受“生产路径 + 实验路径并存”的现实，不追求过度抽象。

## Migration Plan

1. 先通过 OpenSpec 把桌面交易正式定义为 capability，并与 API 管理层并列。
2. 后续新增一个实现型 change，建立 `TradeManager` 或等价门面。
3. 再新增一个 CLI 收敛型 change，规划 `trade` 二级命令，并保留现有扁平命令兼容。
4. 最后在 task 层把“行情判断 + 下单执行 + 状态回填”做成高频场景流程。

## Open Questions

- `TradeManager` 是否只覆盖平安线路，还是从一开始就为多券商适配做统一抽象？
- `trade` CLI 是否应只暴露稳定命令，而把实验命令保留在扁平入口或 `debug` 子组？
- 交易 profile 是否应单独落到 `runtime/trade-profiles.json`，与 `api-profiles.json` 并列？
- 合同号、状态文件、日志和后续流程回填是否都应由顶层交易 manager 统一治理？
