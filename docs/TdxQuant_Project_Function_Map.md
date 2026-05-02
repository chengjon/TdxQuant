# TdxQuant 项目功能地图

本文面向需要复用本项目的上层系统，用来说明：

- 本项目当前已经实现了什么
- 本项目接下来准备实现什么
- 本项目的边界在哪里
- 上层项目应当把它看成什么类型的工具

## 1. 项目定位

本项目的目标不是单纯做一套 TdxQuant 原始函数封装，而是做成一个可被上层 Python / Rust 量化项目复用的本地工具层。

当前定位可以概括为：

- 通达信本地数据与公式能力封装层
- 通达信实时订阅与客户端联动能力层
- 桌面自动化交易执行辅助层
- 面向日常调用的 task / report / catalog 统一入口层

更准确地说，本项目在架构上是三条并行能力线：

- 查询与运行时主线：`TdxApiManager`
- 场景任务与日常入口主线：`TdxTaskManager`、`report`、`catalog`
- 桌面自动化交易主线：`TdxTradeManager`

也可以把当前能力树直接理解为：

```text
TdxQuant
├── Query / Runtime
│   ├── market
│   ├── meta
│   ├── financial
│   ├── transaction
│   ├── formula
│   ├── block
│   ├── runtime
│   ├── runtime subscription session
│   └── provider fixtures
├── Task / Report / Catalog
│   ├── TdxTaskManager
│   ├── report
│   └── catalog
└── Desktop Trade
    ├── TdxTradeManager
    ├── trade profiles
    ├── trade presets
    ├── state backfill
    └── event log
```

## 2. 已实现功能地图

### 2.1 查询与运行时主线

当前项目已经形成统一查询门面 `TdxApiManager`，并按业务域拆分了标准能力。

#### `market`

已实现：

- K 线数据
- 市场快照
- 全推 / 分笔快照
- 个股静态资料
- 扩展静态资料
- 可转债资料

典型入口：

- Python：`TdxApiManager.market.*`
- CLI：`tdxquant api ...`

#### `meta`

已实现：

- 股票列表
- 板块列表
- 板块成分股
- 股本信息
- 单股专项数据
- 分红送转因子
- IPO / 新股新债资料

#### `formula`

已实现：

- 公式数据格式化
- 公式数据写入
- 公式数据源信息写入
- 公式数据读取
- 指标计算
- 选股计算
- 专家公式计算
- 批量选股
- 批量指标计算
- 稳定 `formula.screen` provider contract

这部分是项目的重要差异化能力，因为它直接承接通达信原生公式体系。

当前推荐给上层系统优先对接的正式公式入口是：

- Python：`TdxApiManager.formula.screen(...)`
- CLI：`tdxquant api formula-screen ...`
- CLI：`tdxquant tdx-formula-screen ...`

旧 `formula-mul-xg / process_mul_xg(...)` 仍保留，但更适合原始桥接、调试和兼容场景。

#### `block`

已实现：

- 读取自定义板块
- 创建板块
- 删除板块
- 重命名板块
- 清空板块
- 写入板块成分
- `block_mutation` 标准摘要
- 本地 audit log artifact
- 可选 `mutation_key` 关联键

#### `runtime`

已实现：

- 刷新缓存
- 刷新 K 线
- 获取交易日历
- 下载文件
- 发送客户端预警

#### `provider fixtures`

已实现：

- 内置 provider replay fixture bundle
- 稳定 fixture manifest / loader
- `json` / `jsonl` sample 资产
- `formula.screen` / `doctor` / `block mutation` / `subscription event` / `subscription watch run artifact` representative fixtures

#### `financial`

已实现：

- 专业财务数据查询
- 按日期查询专业财务数据

#### `transaction`

已实现：

- 股票交易统计数据
- 按日期查询股票交易统计数据
- 板块交易统计数据
- 按日期查询板块交易统计数据
- 市场交易统计数据
- 按日期查询市场交易统计数据

#### `runtime subscription session`

已实现：

- 打开持久订阅 session
- 订阅实时行情
- 退订实时行情
- 查询当前 session 的订阅列表
- 关闭 session

当前入口形式：

- Python：`TdxApiManager.runtime.open_subscription_session()`

这部分已经解决了“订阅必须依赖持久会话”的底层问题，并已经上收出首个稳定前台 task：

- Python：`TdxTaskManager.subscription_watch(...)`
- CLI：`tdxquant task subscription-watch ...`

### 2.2 场景任务层

当前项目已经有 `TdxTaskManager` 骨架和首批稳定任务。

已实现或已形成稳定入口的任务包括：

- `sector_research`
- `formula_scan`
- `watchlist_overview`
- `watchlist_export`
- `sector_formula_scan`
- `sector_research_export`
- `subscription_watch`
- `refresh_environment`
- `trade_buy`
- `trade_submit_once`
- `trade_submit_ready`
- `trade_confirm_current`
- `guarded_trade_buy`
- 稳定交易 task 已透传 `submission_key` 与 `max_price`
- `task run --preset ...` 已支持同一组交易安全参数并保留显式 CLI 覆盖

这层的目标不是补充新的底层函数，而是把多步骤流程收口成稳定任务。

### 2.3 报表与日常入口层

当前项目已具备以下高层入口：

#### `report`

已实现：

- `ledger`
- `daily`
- `lookup`
- `period`

#### `catalog`

已实现：

- `catalog list`
- `catalog run`
- `catalog plan`
- bundle 支持
- bundle step 选择
- label 过滤
- summary view

`catalog` 的定位是统一日常入口目录，而不是新的业务管理层。

### 2.4 桌面自动化交易主线

当前项目已经把桌面交易独立为单独 capability，不再混入查询 API 主线。

已实现的能力锚点包括：

- `tdxquant/desktop/`
  - UIA
  - Win32
  - HID
  - 窗口与控件级自动化
- `tdxquant/brokers/`
  - 券商适配器
- `tdxquant/trade/`
  - `TdxTradeManager`
  - trade profiles
  - trade presets
- `tdxquant/trader/`
  - `TradeService`
  - `SecuritiesTraderGateway`
  - `PingAnDesktopTraderGateway`
  - canonical trader store

当前已落地的交易方向能力包括：

- 平安证券买入流程
- 平安证券卖出流程
- 平安证券 submit-once 流程
- 平安证券 sell submit-once 流程
- 买入确认推进
- 结果窗关闭
- 交易状态回填
- 日志与结果文件输出
- `submission_key` 请求关联键
- 前置 `max_price` 风险门
- 标准化 `trade_safety` 安全摘要
- 稳定性 / 副作用分级结果字段
- 真正幂等的 `submission_key` ledger
- 同 key 同请求重复提交短路返回
- 同 key 异请求冲突拒绝
- 实验开关版本的 Win32 顶层窗口枚举方案
- trade profiles
- trade presets
- 固定状态文件 `runtime/pingan-last-order.json`
- 追加事件日志 `runtime/pingan-order-events.jsonl`
- 固定 submission ledger `runtime/pingan-submission-ledger.jsonl`
- 不可变单次审计目录 `runtime/trade-audits/`
- 标准化 `trade_audit` 摘要与审计 artifact

当前交易主线的稳定入口可以理解为：

- Python：
  - `TdxTradeManager.pingan.health(...)`
  - `TdxTradeManager.pingan.preflight(...)`
  - `TdxTradeManager.pingan.submit_ready(...)`
  - `TdxTradeManager.pingan.confirm_current(...)`
 - `TdxTradeManager.pingan.dialog_readiness(...)`
  - `TdxTradeManager.pingan.buy(...)`
  - `TdxTradeManager.pingan.sell(...)`
  - `TdxTradeManager.pingan.buy_submit_once(...)`
  - `TdxTradeManager.pingan.sell_submit_once(...)`
- CLI：
  - `tdxquant trade health ...`
  - `tdxquant trade preflight ...`
  - `tdxquant trade submit-ready ...`
  - `tdxquant trade confirm-current ...`
  - `tdxquant trade dialog-readiness ...`
  - `tdxquant trade buy ...`
  - `tdxquant trade sell ...`
  - `tdxquant trade submit-once ...`
  - `tdxquant trade sell-submit-once ...`
  - `tdxquant trade run --preset ...`
  - 兼容旧入口 `pingan-buy` / `pingan-buy-submit-once`

当前真实交易执行主线已经明确收口到 `PingAN + HID`。这条线的目标是“辅助实盘执行”，不是把 TdxQuant 当成标准交易 API。

与 task 层的当前衔接状态是：

- Python：
  - `TdxTaskManager.trade_buy(...)`
  - `TdxTaskManager.trade_sell(...)`
  - `TdxTaskManager.trade_submit_once(...)`
  - `TdxTaskManager.trade_sell_submit_once(...)`
  - `TdxTaskManager.trade_submit_ready(...)`
  - `TdxTaskManager.trade_confirm_current(...)`
  - `TdxTaskManager.guarded_trade_buy(...)`
- CLI：
  - `tdxquant task trade-buy ...`
  - `tdxquant task trade-sell ...`
  - `tdxquant task trade-submit-once ...`
  - `tdxquant task trade-sell-submit-once ...`
  - `tdxquant task trade-submit-ready ...`
  - `tdxquant task trade-confirm-current ...`
 - `tdxquant task guarded-trade-buy ...`
  - `tdxquant task run --preset ...`

这些稳定 task workflow 现在已经透传：

- `submission_key`
- `max_price`
- 底层 `trade_safety` 摘要
- submission ledger artifact 可见性

其中，split-step task workflow 已经直接承接底层稳定边界：

- `trade_submit_ready`：可选 refresh 后推进到确认框边界
- `trade_confirm_current`：推进当前确认框并返回结果窗摘要

并行引入的证券交易主线则是：

- Python：
  - `TradeService.connect(...)`
  - `TradeService.heartbeat(...)`
  - `TradeService.place_order(...)`
  - `TradeService.query_order(...)`
  - `TradeService.query_trades(...)`
  - `TradeService.sync_today_trades(...)`
- CLI：
  - `tdxquant trade order-place ...`
  - `tdxquant trade order-query ...`
  - `tdxquant trade trade-query ...`
  - `tdxquant trade buy ...`
  - `tdxquant trade sell ...`
  - `tdxquant trade submit-once ...`
  - `tdxquant trade sell-submit-once ...`

这条新主线当前的边界是：

- 只覆盖普通 A 股现货限价 `buy/sell`
- 只保证 canonical tracked-order / trade query，不承诺完整券商委托页/成交页抓取
- `trade buy` / `trade sell` / `trade submit-once` / `trade sell-submit-once` 已转发到 canonical `TradeService`
- `trade submit-ready` / `trade confirm-current` 继续保留为 PingAn 桌面边界命令

新主线的 canonical runtime 产物位于：

- `runtime/trader/order-events.jsonl`
- `runtime/trader/order-snapshots.jsonl`
- `runtime/trader/trade-fills.jsonl`
- `runtime/trader/latest-orders.json`
- `runtime/trader/latest-trades.json`

迁移期内，旧产物仍然保留：

- `runtime/pingan-last-order.json`
- `runtime/pingan-order-events.jsonl`
- `runtime/pingan-submission-ledger.jsonl`
- `runtime/trade-audits/`

## 3. 正在推进或下一步准备实现的能力

### 3.1 订阅能力产品化

底层 session 和第一版前台 task 都已经完成，当前可直接使用：

- `task subscription-watch`
- 持有持久订阅 session
- 连续接收回调
- 每次运行创建独立 `run_id` 目录
- canonical `events.jsonl`
- 维护 `status.json` / `summary.json` / `manifest.json`
- 兼容 `CSV` 导出
- 支持 `Ctrl+C` 优雅退出
- 输出摘要结果与运行统计

后续剩余工作主要转向：

- daemon / `start / stop / status / list`
- replay / fake fixture

### 3.2 统一治理补齐

虽然能力面已经扩了很多，但跨域规范仍需继续补齐：

- 统一错误模型
- 统一耗时记录
- 统一日志结构
- 统一 JSON / CSV 输出结构
- 统一 profile / preset / bundle 组织方式
- 统一导出目录、日志目录、缓存目录、状态文件目录

其中，`formula.screen` 已经成为第一条稳定业务 contract，后续剩余重点会转向：

- replay / fake / contract test 夹具
- 更强的 `block` 重复写保护与同步策略

其中第一版 replay fixture bundle 也已落地，后续剩余重点收缩为：

- 更高一层的 fake provider mode
- transport-level replay / integration hardening

### 3.3 桌面交易安全治理补齐

交易主线当前已经补齐第一版安全治理切片：

- 稳定、无副作用的 `trade health` / broker-runtime preflight
- 稳定、无副作用的 `trade preflight` / single-request readiness summary
- 稳定、会停在确认框前的 `trade submit-ready` / pre-confirm boundary summary
- 稳定、会推进当前确认框的 `trade confirm-current` / current-confirm + optional result-close summary
- 稳定、无副作用的 `trade dialog-readiness` / confirm-result lookup readiness summary
- `trade_safety` 标准摘要
- `beta` / `local_state_mutating` / `live_side_effecting` 分级字段
- 幂等型 `submission_key`
- 基于请求校验和 `max_price` 的前置风险门
- durable submission ledger
- 同 key 重复请求短路与冲突拒绝
- 不可变 `trade_audit` JSON artifact
- `trade_audit` 与 state / event artifact 的关联回灌
- `TdxTaskManager.trade_audit_lookup(...)`
- `TdxTaskManager.trade_audit_daily_report(...)`
- `TdxTaskManager.trade_audit_period_report(...)`
- `tdxquant task trade-audit-lookup ...`
- `tdxquant task trade-audit-daily-report ...`
- `tdxquant task trade-audit-period-report ...`
- `tdxquant report audit-lookup ...`
- `tdxquant report audit-daily ...`
- `tdxquant report audit-period ...`
- `trade_audit` daily / period workflow 支持单状态 `status` 和多状态 `statuses` OR 过滤
- CLI 支持 `--status-any ...` 多次传入异常状态集合
- `trade_audit` daily / period workflow 支持单方法 `method` 和多方法 `methods` OR 过滤
- CLI 支持 `--method-any ...` 多次传入方法集合
- `trade_audit` 日常入口已覆盖 `confirm_current + rejected|failed` 的多维异常视角
- `trade_audit` 日常入口已覆盖 `buy_submit_once + rejected|failed` 的多维异常视角
- `trade_audit` 日常入口已覆盖 `buy + rejected|failed` 的多维异常视角
- `trade_audit` 日常入口已覆盖 submit path `buy_submit_once + confirm_current + rejected|failed` 的多维异常视角
- `trade_audit` 日常入口已覆盖 broker-scoped submit path `pingan + buy_submit_once + confirm_current + rejected|failed` 的多维异常视角
- report presets：`audit-daily-review` / `audit-daily-confirmed` / `audit-daily-rejected` / `audit-daily-replayed` / `audit-daily-failed` / `audit-daily-exceptions` / `audit-daily-confirm-exceptions` / `audit-daily-submit-once-exceptions` / `audit-daily-buy-exceptions` / `audit-daily-submit-path-exceptions` / `audit-daily-pingan-submit-path-exceptions` / `audit-period-review` / `audit-period-confirmed` / `audit-period-rejected` / `audit-period-replayed` / `audit-period-failed` / `audit-period-exceptions` / `audit-period-confirm-exceptions` / `audit-period-submit-once-exceptions` / `audit-period-buy-exceptions` / `audit-period-submit-path-exceptions` / `audit-period-pingan-submit-path-exceptions`
- catalog entries：`audit-daily-review` / `audit-daily-confirmed` / `audit-daily-rejected` / `audit-daily-replayed` / `audit-daily-failed` / `audit-daily-exceptions` / `audit-daily-confirm-exceptions` / `audit-daily-submit-once-exceptions` / `audit-daily-buy-exceptions` / `audit-daily-submit-path-exceptions` / `audit-daily-pingan-submit-path-exceptions` / `audit-period-review` / `audit-period-confirmed` / `audit-period-rejected` / `audit-period-replayed` / `audit-period-failed` / `audit-period-exceptions` / `audit-period-confirm-exceptions` / `audit-period-submit-once-exceptions` / `audit-period-buy-exceptions` / `audit-period-submit-path-exceptions` / `audit-period-pingan-submit-path-exceptions`
- audit bundles：`audit-diagnostics` / `audit-rejection-diagnostics` / `audit-confirmed-review` / `audit-replay-review` / `audit-failure-diagnostics` / `audit-exception-diagnostics` / `audit-confirm-exception-diagnostics` / `audit-submit-once-exception-diagnostics` / `audit-buy-exception-diagnostics` / `audit-submit-path-exception-diagnostics` / `audit-pingan-submit-path-exception-diagnostics`
- task presets：`submit-ready-default` / `confirm-current-default`
- split-step catalog entries：`task-submit-ready` / `task-confirm-current`
- split-step bundles：`confirm-audit-review` / `confirm-complete-review` / `confirm-exception-review` / `submit-once-exception-review` / `guarded-buy-exception-review` / `confirm-submit-path-exception-review` / `confirm-pingan-submit-path-exception-review`
- 基于 `audit_id` / `contract_no` / `submission_key` / `code` 的稳定审计查询
- 唯一命中回填完整 audit，候选查询按时间倒序返回
- 基于本地日期的稳定单日审计聚合
- 基于闭区间的稳定审计聚合

当前剩余重点进一步收缩为：

- `trade_audit` 更高阶的 broker / method / status 多维 review / diagnostics 组合扩展
- 分步交易 workflow 的更多日常 follow-up 组合扩展

### 3.4 场景任务继续沉淀

后续会继续把高频流程沉淀成稳定任务，而不是让调用方自己拼原子命令，例如：

- 订阅监控任务
- 公式筛选后落板块任务
- 周期查询转报表任务
- 组合查询任务

### 3.5 日常入口继续收口

后续 `catalog` 的工作重点应是收口已稳定能力，而不是扩成新的治理层：

- 更好发现可用入口
- 更好预览执行计划
- 更好管理 preset / bundle

## 4. 规划中的明确边界

### 4.1 本项目要深耕的方向

- 通达信本地数据查询
- 通达信公式引擎
- 实时订阅与事件处理
- 自定义板块治理
- 客户端消息 / 预警 / 文件联动
- 桌面自动化交易辅助
- task / report / catalog 的日常调用入口

### 4.2 本项目不应强行承担的方向

- 不以“大而全的 broker-native 标准化券商 API 平台”作为项目主线
- 仅在受控范围内建设证券 `TraderGateway` 主线；M1 只覆盖普通 A 股现货限价买卖与本地 tracked-order / trade query
- 不优先建设完整的撤单 / 资金 / 持仓 / 原生推送 API 体系
- 不把本项目做成第二套完整策略引擎
- 不让 `catalog` 反向主导底层架构

换句话说，本项目更像：

- 通达信本地能力适配层
- 日常研究与监控工具层
- 桌面交易辅助执行层

而不是完整的策略中心或交易中心。

## 5. 推荐的上层使用方式

从当前方向看，本项目最终需要同时服务两类上层项目：

- Python 量化综合项目
- Rust 量化综合项目

因此，本项目后续很可能需要支持以下一种或多种复用方式：

- Python 直接调用 manager / task
- Rust 通过 CLI + JSON 结果协议调用
- 通过稳定的状态文件 / JSONL 事件文件对接
- 通过未来的本地常驻服务统一复用

但具体采用哪种方式，需要根据上层项目的实际约束来定。

## 6. 当前建议的总体判断

如果把本项目当作两个上层项目共用工具，最合适的理解是：

- 它是通达信本地能力工具箱
- 它提供标准化查询、公式、订阅、板块与客户端联动能力
- 它补足桌面自动化交易执行能力
- 它通过 task / report / catalog 提供更稳定的日常入口

一句话总结：

本项目正在被建设成“可复用于多个上层量化系统的通达信本地能力中间层”，而不是单一脚本集合或单一交易程序。
