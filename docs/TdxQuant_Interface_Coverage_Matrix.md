# TdxQuant 接口能力覆盖矩阵

> 状态源说明：本文是接口覆盖对照矩阵，不是功能状态注册表。
>
> 当前“已实现 / 部分实现 / 已设计待实现 / 非目标边界”的唯一准入口是根目录 [`FUNCTION_TREE.md`](../FUNCTION_TREE.md)。
>
> 本文中的“已覆盖 / 部分覆盖 / 未覆盖 / 不纳入当前 query manager”只说明接口覆盖口径；如与 `FUNCTION_TREE.md` 的功能状态不一致，以 `FUNCTION_TREE.md` 为准。

本文对照 [docs/TdxQuant接口说明文档.md](/opt/iflow/TdxQuant/docs/TdxQuant接口说明文档.md:1)，梳理当前项目对文档中公开能力的覆盖情况。

统计口径：

- 以“当前项目是否已有 bridge 封装、manager 入口、嵌套 CLI 入口或稳定高层 facade”为准。
- 不把底层 `tqcenter` 理论支持但本项目未封装的能力算作“已覆盖”。
- 将“应独立于 query manager 的能力”单独列为“不纳入当前 manager 主线”。

状态定义：

- `已覆盖`
  - 已进入 `TdxApiManager` / `TdxTaskManager` / `TdxTradeManager` 或已有稳定二级 CLI 入口
- `部分覆盖`
  - 项目里已有部分实现锚点，但尚未完整进入标准 manager + nested CLI 路径
- `未覆盖`
  - 当前项目未形成 bridge 封装或顶层入口
- `不纳入当前 query manager`
  - 能力应归入桌面交易独立 capability，或属于回测 / 模拟 / 策略运行体系，而非当前查询主线

## 1. 已覆盖能力

| 文档能力 | 当前状态 | 当前项目入口 | 归属层 | 说明 |
| --- | --- | --- | --- | --- |
| `get_market_data` | 已覆盖 | `TdxApiManager.market.kline` / `api kline` / `tdx-data-kline` | `market` | 标准 nested CLI 与 Python manager 已对齐 |
| `get_market_snapshot` | 已覆盖 | `TdxApiManager.market.market_snapshot` / `api market-snapshot` / `tdx-data-market-snapshot` | `market` | 已支持字段筛选 |
| Tick / 分笔数据 (`get_full_tick`) | 已覆盖 | `TdxApiManager.market.full_tick` / `api full-tick` / `tdx-data-snapshot` | `market` | `api snapshot` 继续保留为兼容入口 |
| `get_stock_info` | 已覆盖 | `TdxApiManager.market.stock_info` / `api stock-info` / `tdx-data-stock-info` | `market` | 文档更新项已纳入 |
| `get_more_info` | 已覆盖 | `TdxApiManager.market.more_info` / `api more-info` / `tdx-data-more-info` | `market` | 已支持字段筛选 |
| `get_cb_info` | 已覆盖 | `TdxApiManager.market.cb_info` / `api cb-info` / `tdx-data-cb-info` | `market` | 已支持字段筛选 |
| `get_stock_list` | 已覆盖 | `TdxApiManager.meta.stock_list` / `api stock-list` / `tdx-data-stock-list` | `meta` | 已支持 `list_type` |
| `get_sector_list` | 已覆盖 | `TdxApiManager.meta.sector_list` / `api sector-list` / `tdx-data-sector-list` | `meta` | 已支持 `list_type` |
| `get_stock_list_in_sector` | 已覆盖 | `TdxApiManager.meta.sector_stocks` / `api sector-stocks` / `tdx-data-sector-stocks` | `meta` | 项目命名为 `sector_stocks` |
| `get_gb_info` | 已覆盖 | `TdxApiManager.meta.gb_info` / `api gb-info` / `tdx-data-gb-info` | `meta` | 支持 `date_list + count` |
| `get_gp_one_data` | 已覆盖 | `TdxApiManager.meta.gp_one_data` / `api gp-one` / `tdx-data-gp-one` | `meta` | 用作多个 task 的底层原子能力 |
| `get_divid_factors` | 已覆盖 | `TdxApiManager.meta.divid_factors` / `api divid-factors` / `tdx-data-divid-factors` | `meta` | 先按参考数据并入 `meta` 域 |
| `get_ipo_info` | 已覆盖 | `TdxApiManager.meta.ipo_info` / `api ipo-info` / `tdx-data-ipo-info` | `meta` | 新股/新发债申购参考信息已进入标准 manager |
| `get_financial_data` | 已覆盖 | `TdxApiManager.financial.financial_data` / `api financial-data` / `tdx-data-financial` | `financial` | 专业财务时间区间查询已独立进入 `financial` 子域 |
| `get_financial_data_by_date` | 已覆盖 | `TdxApiManager.financial.financial_data_by_date` / `api financial-data-by-date` / `tdx-data-financial-by-date` | `financial` | 指定日期专业财务查询已进入标准 manager |
| `get_gpjy_value` | 已覆盖 | `TdxApiManager.transaction.stock_transaction_data` / `api stock-transaction-data` / `tdx-data-stock-transaction` | `transaction` | 股票交易数据时间区间查询已独立进入 `transaction` 子域 |
| `get_gpjy_value_by_date` | 已覆盖 | `TdxApiManager.transaction.stock_transaction_data_by_date` / `api stock-transaction-data-by-date` / `tdx-data-stock-transaction-by-date` | `transaction` | 指定日期股票交易数据查询已进入标准 manager，并保留 `year=0,mmdd=0` 语义 |
| `get_bkjy_value` | 已覆盖 | `TdxApiManager.transaction.sector_transaction_data` / `api sector-transaction-data` / `tdx-data-sector-transaction` | `transaction` | 板块交易数据时间区间查询已沿 `transaction` 子域继续扩展 |
| `get_bkjy_value_by_date` | 已覆盖 | `TdxApiManager.transaction.sector_transaction_data_by_date` / `api sector-transaction-data-by-date` / `tdx-data-sector-transaction-by-date` | `transaction` | 指定日期板块交易数据查询已进入标准 manager，并保留 `year=0,mmdd=0` 语义 |
| `get_scjy_value` | 已覆盖 | `TdxApiManager.transaction.market_transaction_data` / `api market-transaction-data` / `tdx-data-market-transaction` | `transaction` | 市场交易数据时间区间查询已沿 `transaction` 子域收口，但不再要求证券代码列表 |
| `get_scjy_value_by_date` | 已覆盖 | `TdxApiManager.transaction.market_transaction_data_by_date` / `api market-transaction-data-by-date` / `tdx-data-market-transaction-by-date` | `transaction` | 指定日期市场交易数据查询已进入标准 manager，并保留 `year=0,mmdd=0` 语义 |
| `refresh_cache` | 已覆盖 | `TdxApiManager.refresh_cache` / `api refresh-cache` / `tdx-refresh-cache` | `manager` | 当前为 manager 直出能力 |
| `get_trading_dates` | 已覆盖 | `TdxApiManager.runtime.trading_dates` / `api trading-dates` / `tdx-get-trading-dates` | `runtime` | 归入公共运行时查询子域 |
| `refresh_kline` | 已覆盖 | `TdxApiManager.runtime.refresh_kline` / `api refresh-kline` / `tdx-refresh-kline` | `runtime` | 与 `refresh_cache` 保持语义分离 |
| `download_file` | 已覆盖 | `TdxApiManager.runtime.download_file` / `api download-file` / `tdx-download-file` | `runtime` | 返回结构化结果并提示 Windows 下载目录 |
| `send_warn` | 已覆盖 | `TdxApiManager.runtime.send_warn` / `api send-warn` / `tdx-send-warn` | `runtime` | 客户端预警发送已进入标准 manager 与 CLI，CLI 使用语义化 `volume` 参数并映射到底层 `volum_list` |
| `get_user_sector` | 已覆盖 | `TdxApiManager.block.user_sectors` / `api user-sectors` / `tdx-get-user-sector` | `block` | 自定义板块列表读取归入 `block` 资源域 |
| `create_sector` | 已覆盖 | `TdxApiManager.block.create_sector` / `api create-sector` / `tdx-create-sector` | `block` | 自定义板块创建已进入标准 manager，并返回 `block_mutation` 与 audit artifact |
| `delete_sector` | 已覆盖 | `TdxApiManager.block.delete_sector` / `api delete-sector` / `tdx-delete-sector` | `block` | 自定义板块删除已进入标准 manager，并返回 `block_mutation` 与 audit artifact |
| `rename_sector` | 已覆盖 | `TdxApiManager.block.rename_sector` / `api rename-sector` / `tdx-rename-sector` | `block` | 自定义板块重命名已进入标准 manager，并返回 `block_mutation` 与 audit artifact |
| `clear_sector` | 已覆盖 | `TdxApiManager.block.clear_sector` / `api clear-sector` / `tdx-clear-sector` | `block` | 与 `send_user_block(..., stocks=[])` 保持显式分离，并返回 `block_mutation` 与 audit artifact |
| `send_user_block` | 已覆盖 | `TdxApiManager.block.send_user_block` / `api send-user-block` / `tdx-send-user-block` | `block` | 已从 `meta` 中独立出来，并支持 `mutation_key` 与本地审计 |
| `formula_format_data` | 已覆盖 | `TdxApiManager.formula.format_data` / `api formula-format-data` / `tdx-formula-format-data` | `formula` | 已纳入标准 manager |
| `formula_set_data` | 已覆盖 | `TdxApiManager.formula.set_data` / `api formula-set-data` / `tdx-formula-set-data` | `formula` | 已纳入标准 manager |
| `formula_set_data_info` | 已覆盖 | `TdxApiManager.formula.set_data_info` / `api formula-set-data-info` / `tdx-formula-set-data-info` | `formula` | 已纳入标准 manager |
| `formula_get_data` | 已覆盖 | `TdxApiManager.formula.get_data` / `api formula-get-data` / `tdx-formula-get-data` | `formula` | 已纳入标准 manager |
| `formula_zb` | 已覆盖 | `TdxApiManager.formula.zb` / `api formula-zb` / `tdx-formula-zb` | `formula` | 已支持 `xsflag` |
| `formula_xg` | 已覆盖 | `TdxApiManager.formula.xg` / `api formula-xg` / `tdx-formula-xg` | `formula` | 已纳入标准 manager |
| `formula_exp` | 已覆盖 | `TdxApiManager.formula.exp` / `api formula-exp` / `tdx-formula-exp` | `formula` | 已纳入标准 manager |
| `formula_process_mul_xg` | 已覆盖 | `TdxApiManager.formula.process_mul_xg` / `api formula-mul-xg` / `task formula-scan` | `formula` + `task` | 已有高层扫描任务封装 |
| `formula_process_mul_zb` | 已覆盖 | `TdxApiManager.formula.process_mul_zb` / `api formula-mul-zb` | `formula` | 已纳入标准 manager |

## 2. 部分覆盖能力

这些能力已经有稳定的 bridge + manager 路径，并且已经有 `subscription-watch` 前台任务与 worker bridge 控制面；剩余缺口主要是 query-style one-shot CLI、transport wrapper 和更高阶 replay / fake provider。

| 文档能力 | 当前状态 | 当前入口 | 归属层 | 说明 |
| --- | --- | --- | --- | --- |
| `subscribe_hq` | 部分覆盖 | `TdxApiManager.runtime.open_subscription_session() -> session.subscribe_hq(...)`; `TdxTaskManager.subscription_watch(...)`; `task subscription-watch` | `runtime session` / `task` | 已通过持久 session 进入 manager 管理层，并已提供稳定前台 task；仍未暴露为 query-style one-shot CLI |
| `unsubscribe_hq` | 部分覆盖 | `TdxApiManager.runtime.open_subscription_session() -> session.unsubscribe_hq(...)`; `TdxTaskManager.subscription_watch(...)` | `runtime session` / `task` | 与订阅共用同一持久 session；foreground task 结束时会执行 unsubscribe + close |
| `get_subscribe_hq_stock_list` | 部分覆盖 | `TdxApiManager.runtime.open_subscription_session() -> session.get_subscribe_hq_stock_list()` | `runtime session` | 返回当前活跃 session 的订阅列表；当前 `subscription-watch` 不单独暴露 list 控制面 |

## 3. 未覆盖能力

这些能力在接口说明文档中存在，但当前项目尚未形成稳定 bridge + manager + nested CLI 路径。

| 文档能力 | 当前状态 | 建议归属层 | 优先级 | 说明 |
| --- | --- | --- | --- | --- |
## 4. 不纳入当前 Query Manager 主线的能力

| 文档能力 / 场景 | 当前状态 | 当前项目定位 | 说明 |
| --- | --- | --- | --- |
| 回测 | 不纳入当前 query manager | 暂未形成独立子系统 | 接口说明文档把它作为平台场景，但当前项目未建设回测引擎 |
| 模拟交易 | 不纳入当前 query manager | 暂未形成独立子系统 | 当前项目主做查询封装与桌面交易能力，不含模拟撮合体系 |
| 券商实盘交易总线 | 不纳入当前 query manager | 用桌面自动化交易 capability 替代 | 当前项目实际落地的是 `TdxTradeManager` + Ping An 桌面自动化路径 |
| 策略运行 / tqcenter 直接脚本宿主 | 不纳入当前 query manager | 保留底层可用，不纳入本轮 manager 规划 | 当前重点不是重建官方策略运行框架 |

## 5. 当前项目新增的高层能力

这些能力不直接来自接口说明文档中的官方函数名，但已经是当前项目的重要稳定入口：

- `TdxTaskManager`
  - `sector_research`
  - `formula_scan`
  - `watchlist_overview`
  - `watchlist_export`
  - `sector_formula_scan`
  - `sector_research_export`
  - `refresh_environment`
  - `trade_buy`
  - `trade_submit_once`
  - `guarded_trade_buy`
- `report` 二级 CLI
  - `ledger`
  - `daily`
  - `lookup`
  - `period`
- `TdxTradeManager`
  - `pingan.buy(...)`
  - `pingan.buy_submit_once(...)`
- `catalog`
  - 统一日常 entry / bundle 目录层

这些能力属于“项目上层编排与收口”，不应反向定义底层官方接口覆盖状态。

## 6. 建议的下一批实现包

### 包 1：Query CLI 对齐包

目标：

- 补齐 `api kline`
- 显式设计 `full-tick` / 分笔接口

理由：

- 当前 Python manager 已经有 `kline`，但标准 `api ...` CLI 还没对齐
- 这是“已有底层实现，缺标准入口”的最低风险补齐项

### 包 2：Runtime / 公共查询能力包

当前状态：

- 已完成

已落地入口：

- `TdxApiManager.runtime.trading_dates(...)`
- `TdxApiManager.runtime.refresh_kline(...)`
- `TdxApiManager.runtime.download_file(...)`
- `api trading-dates`
- `api refresh-kline`
- `api download-file`
- `tdx-get-trading-dates`
- `tdx-refresh-kline`
- `tdx-download-file`

目标：

- `get_trading_dates`
- `refresh_kline`
- `download_file`

理由：

- 这三类能力更像公共运行时或缓存治理，不宜硬塞进现有单域业务对象
- 目前已通过独立 `runtime` 子域完成第一轮标准入口收口，后续只需继续补治理细节

### 包 3：Block 生命周期包

当前状态：

- 已完成

已落地入口：

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
- `tdx-get-user-sector`
- `tdx-create-sector`
- `tdx-delete-sector`
- `tdx-rename-sector`
- `tdx-clear-sector`

目标：

- `get_user_sector`
- `create_sector`
- `delete_sector`
- `rename_sector`
- `clear_sector`

理由：

- 当前 `block` 资源域已经从“只支持 `send_user_block`”扩展为完整生命周期闭环
- 当前 `block` 写动作已经补入 `block_mutation` 摘要、本地 audit artifact 与可选 `mutation_key`
- 后续若再增加板块能力，应继续沿 `block` 资源域演进，而不是回退到 `meta`

### 包 4：财务 / 交易数据面包

当前状态：

- 已拆分

#### 包 4A：参考数据子包

当前状态：

- 已完成

已落地入口：

- `TdxApiManager.meta.divid_factors(...)`
- `TdxApiManager.meta.ipo_info(...)`
- `api divid-factors`
- `api ipo-info`
- `tdx-data-divid-factors`
- `tdx-data-ipo-info`

说明：

- 本子包先收口低风险参考数据，避免直接把专业财务和交易数据面一次性做大。

#### 包 4B：专业财务与交易数据面子包

当前状态：

- 已完成前两步

已落地入口：

- `TdxApiManager.financial.financial_data(...)`
- `TdxApiManager.financial.financial_data_by_date(...)`
- `api financial-data`
- `api financial-data-by-date`
- `tdx-data-financial`
- `tdx-data-financial-by-date`
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

理由：

- `financial` 与 `transaction` 子域已经完成当前文档范围内的财务 / 交易数据入口，说明继续独立分域是可行的
- 下一步若继续扩展查询主线，应转向订阅 / 告警或其它未覆盖公共能力，而不是再回到 `market.py`

### 包 5：订阅与告警包

当前状态：

- foreground + bridge slice 已完成，transport / replay / 控制入口仍部分覆盖

已落地入口：

- `TdxApiManager.runtime.send_warn(...)`
- `api send-warn`
- `tdx-send-warn`
- `TdxApiManager.runtime.open_subscription_session()`
- `session.subscribe_hq(...)`
- `session.unsubscribe_hq(...)`
- `session.get_subscribe_hq_stock_list()`

剩余目标：

- query-style one-shot CLI 或等价控制入口
- `HTTP / SSE` 或同类事件流 transport wrapper
- replay / fake provider / delayed playback 形态的订阅测试控制面

理由：

- `send_warn` 是一次性写入动作，已经可以沿 `runtime` 子域平滑收口
- `subscribe_hq / unsubscribe_hq / get_subscribe_hq_stock_list` 已通过持久 session 进入 manager 管理层
- 当前剩余问题已经不是“是否能暴露为日常任务”，而是如何稳定 transport wrapper、replay / fake provider 和 query-style 控制面

## 7. 当前建议结论

如果按“风险最低、收益最高”的顺序继续推进，建议是：

1. `api kline` 和显式 Tick 入口已完成
2. `get_trading_dates / refresh_kline / download_file` 已完成，并已进入 `runtime` 子域
3. `block` 生命周期闭环已完成
4. 参考数据、财务 / 交易数据面、`send_warn`、manager 级订阅持久 session、`subscription-watch` 前台任务与 worker bridge 控制面已完成；下一步应转向订阅 transport wrapper、replay / fake provider、文件导入式 block sync 和更高阶治理入口

这样推进最符合当前总方案中“先补 query manager 覆盖与统一治理，再扩大场景层与入口层”的方向。
