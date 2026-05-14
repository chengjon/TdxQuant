# TdxQuant API 顶层管理体系・整体方案规划

> 状态源说明：本文是 API/manager 分层设计方案，不是功能状态注册表。
>
> 当前“已实现 / 部分实现 / 已设计待实现 / 非目标边界”的唯一准入口是根目录 [`FUNCTION_TREE.md`](../FUNCTION_TREE.md)。
>
> 本文中的“已完成 / 当前 / 规划 / 要求”等表述只用于解释 API 体系设计；如与 `FUNCTION_TREE.md` 的状态注册表不一致，以 `FUNCTION_TREE.md` 为准。

本文是对项目总方案的对齐版，目标是让上位规划与当前已经落地的 `TdxApiManager`、`TdxTaskManager`、`TdxTradeManager`、`catalog` 和桌面交易 capability 保持一致。

## 一、核心设计原则

### 1. 兼容存量

- 现有 `bridge.py` 底层桥接保留。
- 已完成查询接口、桌面自动化链路、CLI 命令全部保留。
- 不重构、不替换、不打断现有可用工作流。

### 2. 解耦堆积

- 终结能力继续堆积在 `bridge.py`、`cli.py` 的无序模式。
- 按业务域、管理层、场景层、入口层和配置层拆边界。

### 3. 双主线治理

- 查询能力与桌面交易能力并行治理。
- `query API management` 和 `desktop trading management` 是并列 capability。
- 桌面交易能力不得继续挂靠到 `TdxApiManager` 上。

### 4. 低风险渐进

- 优先推进纯查询类只读能力和低风险场景封装。
- 交易执行、下单、委托、确认弹窗处理等高风险能力单独演进。
- Windows 真实环境验收依然是桌面交易线的节奏约束。

### 5. 统一规范

- 统一入参、出参、错误处理、日志、耗时、调用范式。
- 同时支撑代码调用和 CLI 调用双入口。
- 统一通过 manager / facade 收口，不鼓励日常直接调用底层桥接函数。

## 二、当前顶层架构定位

当前真实架构应理解为“两条主线 + 一组横切配置层”，而不是把所有能力继续塞进单一 API 体系。

### 1. 查询能力主线

查询主线仍然沿用“底层不动、中间分层、上层统一”的治理方式。

#### 第 1 层：底层桥接与运行时底座

- `tdxquant/api/bridge.py`
  - 只负责原始桥接、原生接口透传。
- runtime / context / helper
  - 负责环境探测、路径解析、公共辅助能力。
  - 不直接承载具体业务语义。

#### 第 2 层：业务域分层

按金融业务语义拆分独立域模块：

- `meta`
  - 股票列表、板块列表、板块成分、静态资料等。
- `market`
  - 单股快照、市场快照、K 线、行情派生查询等。
- `formula`
  - 通达信公式数据准备、指标计算、批量公式执行。
- `block`
  - 自选 / 板块写入与维护能力。

要求：

- 域模块只做单一领域原子能力封装。
- 域模块不直接读 profile 文件。
- 域模块不承担多步骤编排。

#### 第 3 层：统一调度管理层

核心载体：`TdxApiManager`

职责：

- 聚合 `meta / market / formula / block` 四域。
- 统一参数规范、异常封装、结果模型、耗时埋点。
- 作为日常脚本与 Python 代码的统一查询门面。

边界：

- `TdxApiManager` 只治理查询主线。
- 不直接吸纳桌面交易执行逻辑。

#### 第 4 层：场景与日常入口层

这一层已经不只是一种形态，而是三个不同定位的 facade：

- `TdxTaskManager`
  - 面向多接口组合的稳定场景。
- `report`
  - 面向台账、日报、周期统计等结果导向场景。
- `catalog`
  - 统一日常入口目录层。
  - 只做 entry / bundle 索引、执行计划预览和稳定入口收口。
  - 不是新的 manager，也不新增底层业务逻辑。

### 2. 桌面交易能力主线

桌面自动化交易能力是独立 capability，不再视为查询 API 的延长线。

当前实现锚点：

- `tdxquant/desktop/`
  - UIA、Win32、HID、窗口与控件级自动化能力。
- `tdxquant/brokers/`
  - 券商适配器。
- `tdxquant/trade/`
  - `TdxTradeManager`、trade profiles、trade presets。

核心职责：

- 管理桌面交易 profile、执行元数据、耗时包装。
- 管理状态回填、结果日志、事件日志。
- 管理窗口状态、HID/Win32/UIA 协调、确认处理和结果窗处理。

边界：

- 不并入 `TdxApiManager`。
- 保持现有 `pingan-buy`、`pingan-buy-submit-once`、`trade ...` 等命令可用。
- 桌面交易相关实验开关、Windows 专属验证、WSL/Windows 桥接问题单独治理。

### 3. 横切配置与预设层

配置层不是单独业务主线，而是横切在查询和交易之上的参数标准化平面。

核心内容：

- 全局默认值
  - 默认市场、字段集、分页 / 数量、时区等。
- 场景 profile
  - `api` / `task` / `trade` 各自的默认参数模板。
- preset / bundle
  - `report`、`trade`、`task` preset。
  - `catalog` entry / bundle。
- 运行策略
  - 节流、缓存、超时阈值、输出格式偏好。
- 路径约定
  - 导出目录、日志目录、缓存目录、状态文件目录。

## 三、CLI 体系定位

当前 CLI 不再只是一套“原子命令集合”，而是分层入口并存：

- `tdxquant api [原子接口]`
  - 查询主线的标准原子入口。
- `tdxquant task [场景任务]`
  - 组合化高频任务入口。
- `tdxquant report [报表任务]`
  - 结果导向型场景入口。
- `tdxquant trade [交易能力]`
  - 桌面交易 capability 的标准入口。
- `tdxquant catalog [日常目录层]`
  - 统一收口已经稳定的 `task / report / trade` preset 与 bundle。

保留约束：

- 原有扁平命令继续兼容。
- 新二级命令优先支持 `--profile` / preset 风格调用。
- `catalog` 只负责入口收口，不抢 manager 层职责。

## 四、当前进度判断

截至当前版本，整体进度应这样理解：

### 1. 查询主线

已完成：

- `meta / market / formula / block` 已纳入 manager 体系。
- `TdxApiManager` 已形成统一查询门面。
- `api` 二级命令已建立。

部分完成：

- `task` 层已经有稳定骨架和首批高频场景。
- `report` 层已经能承接台账 / 日报 / 周期查询类场景。

仍需继续：

- 对照接口说明文档做能力覆盖盘点。
- 补齐统一输出规范、耗时 / 日志规范、导出规范。

### 2. 桌面交易主线

已完成：

- capability 边界已从查询管理线中分离。
- `TdxTradeManager` 已建立。
- `trade` CLI、trade presets、交易 task 编排已初步形成。

仍在验收 / 迭代：

- `implement-pingan-win32-trading-adapter`
- `implement-tdx-wsl-windows-bridge`

这些工作受真实 Windows 环境和人工确认节奏约束，不应反向拖慢查询主线。

### 3. 日常入口层

已完成：

- `catalog list`
- `catalog run`
- `catalog plan`
- bundle 支持
- bundle step 选择
- label 过滤
- summary view

定位结论：

- `catalog` 已经够用作日常统一入口。
- 后续只应继续收口稳定能力，不应反过来驱动底层架构设计。

## 五、下一步优先级

后续工作不应继续泛化为“所有层一起推进”，而应分主线排优先级。

截至 `2026-05-13`，查询主线覆盖、provider 基础治理、`subscription-watch` foreground + bridge slice、block 基础读写治理和交易安全基础治理都已经完成第一版。当前下一步不应再回到“补更多原子查询函数”，而应围绕 transport / replay / 文件导入 / 写策略 / audit 索引这些集成硬化面推进。

### 第一优先：查询主线收口

1. 对照 `docs/TdxQuant接口说明文档.md` 建立能力覆盖矩阵。
2. 明确：
   - 已覆盖能力
   - 未覆盖能力
   - 不应纳入 manager 的能力
3. 逐项把缺失的查询能力按域纳入 `TdxApiManager`。

### 第二优先：统一治理补齐

1. 补齐 runtime / profile / output 的统一规范。
2. 统一：
   - 错误码
   - 耗时记录
   - 日志策略
   - JSON / CSV 输出结构
   - 配置路径与状态文件路径约定

### 第三优先：场景层稳定化

1. 强化 `TdxTaskManager` 与 `report` 层。
2. 把真实高频流程沉淀成稳定 task / preset。
3. 只有稳定场景才继续上收进 `catalog`。

### 第四优先：catalog 精修而非扩张

`catalog` 后续工作应控制在：

- 更好发现入口
- 更好预览计划
- 更好管理稳定 bundle

不应把它扩成新的业务层或治理层。

### 第五优先：桌面交易线独立推进

1. 继续完成 Windows 手工验收与实验开关验证。
2. 继续优化 TradeManager 侧的状态回填、日志与交易元数据。
3. 保持桌面交易治理边界独立，不并回查询 API 体系。

### 当前进度补记

查询主线在 2026-04-27 已新增独立 `runtime` 子域，当前已纳入：

- `TdxApiManager.runtime.trading_dates(...)`
- `TdxApiManager.runtime.refresh_kline(...)`
- `TdxApiManager.runtime.download_file(...)`
- `TdxApiManager.runtime.send_warn(...)`
- `TdxApiManager.runtime.open_subscription_session()`
- `api trading-dates`
- `api refresh-kline`
- `api download-file`
- `api send-warn`
- `tdx-get-trading-dates`
- `tdx-refresh-kline`
- `tdx-download-file`
- `tdx-send-warn`

同时，manager 级持久订阅 session 已完成第一轮收口，当前支持：

- `session.subscribe_hq(...)`
- `session.unsubscribe_hq(...)`
- `session.get_subscribe_hq_stock_list()`

因此，“查询主线收口”的下一优先项不再是继续补 runtime 的一次性动作，也不再是补订阅底层生命周期本身。`subscription-watch` 前台任务和 worker bridge 控制面已经完成第一版，后续应转向订阅 transport wrapper、replay / fake provider、文件导入式 block sync、写策略硬化和 audit 索引这类集成硬化问题。

同日，`block` 子域也已完成第一轮生命周期闭环，当前已纳入：

- `TdxApiManager.block.user_sectors(...)`
- `TdxApiManager.block.create_sector(...)`
- `TdxApiManager.block.delete_sector(...)`
- `TdxApiManager.block.rename_sector(...)`
- `TdxApiManager.block.clear_sector(...)`
- `api user-sectors`
- `api create-sector`
- `api delete-sector`
- `api rename-sector`
- `api clear-sector`

随后，`block` 写能力也已补入第一版治理 contract，当前 block write 入口统一支持：

- `block_mutation` 标准摘要
- 本地 audit artifact
- 可选 `mutation_key`

因此，查询主线已不需要再回头补自定义板块基础生命周期，后续 block 方向的重点将转为更强的重复写保护与上层同步 task。

随后，`meta` 域已补入一组轻量参考数据能力，当前已纳入：

- `TdxApiManager.meta.divid_factors(...)`
- `TdxApiManager.meta.ipo_info(...)`
- `api divid-factors`
- `api ipo-info`
- `tdx-data-divid-factors`
- `tdx-data-ipo-info`

随后，`financial` 域也已完成第一批专业财务主体入口，当前已纳入：

- `TdxApiManager.financial.financial_data(...)`
- `TdxApiManager.financial.financial_data_by_date(...)`
- `api financial-data`
- `api financial-data-by-date`
- `tdx-data-financial`
- `tdx-data-financial-by-date`

随后，`transaction` 域已完成股票、板块与市场交易数据的标准入口，当前已纳入：

- `TdxApiManager.transaction.stock_transaction_data(...)`
- `TdxApiManager.transaction.stock_transaction_data_by_date(...)`
- `TdxApiManager.transaction.sector_transaction_data(...)`
- `TdxApiManager.transaction.sector_transaction_data_by_date(...)`
- `TdxApiManager.transaction.market_transaction_data(...)`
- `TdxApiManager.transaction.market_transaction_data_by_date(...)`
- `api stock-transaction-data`
- `api stock-transaction-data-by-date`
- `api sector-transaction-data`
- `api sector-transaction-data-by-date`
- `api market-transaction-data`
- `api market-transaction-data-by-date`
- `tdx-data-stock-transaction`
- `tdx-data-stock-transaction-by-date`
- `tdx-data-sector-transaction`
- `tdx-data-sector-transaction-by-date`
- `tdx-data-market-transaction`
- `tdx-data-market-transaction-by-date`

这意味着财务 / 交易数据面在当前接口说明文档范围内已经完成标准入口收口。后续查询主线如果继续推进，不应再回到交易数据分片本身；runtime 层的一次性告警、manager 级订阅持久 session、`subscription-watch` 前台任务和 worker bridge 控制面也已完成，后续重点应转向订阅 transport wrapper、HTTP / SSE 推送语义、replay / fake provider 硬化和 query-style 控制入口。

## 六、关键边界约定

- `bridge.py`
  - 只做原始桥接、原生接口透传，不做复杂场景编排。
- 查询域模块
  - 只做单域原子能力，不跨域组合，不读 profile 文件。
- `TdxApiManager`
  - 只做查询治理，不承载桌面交易执行。
- `TdxTradeManager`
  - 只做桌面交易治理，不承担查询 API 聚合。
- `TdxTaskManager`
  - 允许同时编排 `TdxApiManager` 与 `TdxTradeManager`。
- `report`
  - 是结果导向型场景 facade，不是新的底层能力域。
- `catalog`
  - 不是 manager。
  - 不直接调用 `bridge.py`。
  - 不新增底层业务逻辑。
- 配置 / preset / bundle
  - 只做参数和入口标准化，不写业务逻辑。

## 七、整体总结

这套体系当前应明确为：

`查询主线分层治理 + 桌面交易主线独立治理 + 配置层横切减负 + catalog 统一日常入口`

核心目标不变：

- 底层不动
- 中间分层
- 上层统一
- 场景封装
- 配置减负

但当前执行顺序需要更精确：

- 先补齐 query manager 和统一治理
- 再强化 task / report 场景层
- 最后由 catalog 收口稳定入口
- 桌面交易 capability 继续独立验收与演进
