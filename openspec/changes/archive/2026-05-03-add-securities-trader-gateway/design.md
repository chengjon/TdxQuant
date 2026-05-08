## Context

当前桌面交易能力以 `TdxTradeManager.pingan.*` 为主线，CLI 和 task 入口也直接绑定 `PingAn` 买入提交流程。现有能力已经覆盖健康检查、预检、到确认边界、确认提交和最终审计落盘，但仍缺少 broker-neutral 的证券交易主线，无法把普通 A 股现货限价买卖、统一订单/成交查询和后续同步能力治理成标准接口。

这次变更的目标不是替换现有 PingAn 桌面交易链路，而是在其旁边建立一条并行的证券交易主线。首批范围限制为普通 A 股现货限价 `buy/sell`，并把 `query_order`、`query_trades`、`sync_today_trades` 收口为“新网关本地可追踪订单/成交”的统一查询能力。完整的券商委托页/成交页抓取、账户、持仓和撤单能力留在后续阶段。

## Goals / Non-Goals

**Goals:**
- 新增并行的 `TradeService + TraderGateway` 交易主线，不继续把标准交易能力塞进 `TdxTradeManager.pingan.*`。
- 定义 broker-neutral 的证券交易模型、生命周期状态机和 canonical 事件/快照存储。
- 以 `PingAnDesktopTraderGateway` 作为第一号实现，支持普通 A 股现货限价 `buy/sell` 下单。
- 新增 broker-neutral CLI 命令 `trade order-place`、`trade order-query`、`trade trade-query`。
- 保留现有 `trade buy`、`trade submit-once`、`trade submit-ready`、`trade confirm-current` 作为兼容命令或 PingAn 边界命令，避免一次性破坏现有运维脚本。

**Non-Goals:**
- 不引入期货、CTP、融资融券、可转债、逆回购等非首批证券交易场景。
- 不在 M1 承诺完整的券商委托页/成交页抓取查询。
- 不在 M1 提供原生 push 型 `on_order / on_trade / on_execution_report` 回报；桌面场景仅允许 synthetic event。
- 不立即废弃现有 `pingan-*` 运行时产物和 `TdxTradeManager`。

## Decisions

### 1. 新增 `tdxquant/trader/` 领域层，而不是继续扩展 `TdxTradeManager`

系统将新增 `tdxquant/trader/` 目录，集中承载：
- `models.py`：canonical 交易模型
- `gateway.py`：`SecuritiesTraderGateway` 协议
- `registry.py`：gateway 注册和 broker 解析
- `service.py`：统一交易编排入口
- `store.py`：canonical 订单/成交/事件存储
- `adapters/pingan_desktop.py`：第一号桌面券商实现

选择这一方案，是因为当前 `TdxTradeManager`、CLI 和 task 都是 `PingAn` 特化路径；继续在原对象上叠加 `sell/query/sync` 只会把历史耦合固化得更深。

备选方案：
- 薄封装现有 `TdxTradeManager.pingan.*`
  - 优点：上线快
  - 缺点：新主线仍会被 `PingAn`/`buy-only` 语义污染
- 外部独立交易服务
  - 优点：隔离最好
  - 缺点：超出当前批次范围，运维复杂度过高

### 2. 统一交易模型必须 side-aware，且不复用现有 `OrderRequest`

新主线将引入 `SecurityOrderRequest`、`SecurityOrderSnapshot`、`TradeFill`、`ExecutionReport`、`GatewayCapabilities` 等 canonical 模型。普通 A 股现货限价委托必须显式包含 `side=buy|sell`、`symbol`、`market`、`quantity`、`limit_price`、`client_order_id` 等字段。

价格在 canonical 层使用 `Decimal` 语义，落盘和 CLI/JSON 输出时序列化为字符串，避免 `float` 在交易域带来的精度问题。

备选方案：
- 继续复用当前 `OrderRequest(code, quantity, price)`
  - 被否决，因为它是 `buy-only` 且缺少 broker-neutral 语义

### 3. Canonical 订单状态与桌面边界动作分离

新主线将定义标准订单状态机，例如：
- `CREATED`
- `VALIDATED`
- `SUBMITTING`
- `SUBMITTED`
- `PARTIALLY_FILLED`
- `FILLED`
- `CANCEL_PENDING`
- `CANCELLED`
- `REJECTED`
- `FAILED`

M1 实际落地子集只要求覆盖：
- `CREATED`
- `VALIDATED`
- `SUBMITTING`
- `SUBMITTED`
- `FILLED`
- `REJECTED`
- `FAILED`

`submit_ready`、`confirm_current`、`result_dialog_detected` 等 PingAn 桌面边界动作不会成为 canonical 对外状态，而是落到 adapter 事件或 `ExecutionReport.adapter_step` 中。这样未来更换 broker 时，不需要重写统一状态机。

备选方案：
- 直接把 `submit_ready / confirm_current` 做成公共状态
  - 被否决，因为这会把桌面券商特有边界泄漏到统一接口

### 4. M1 查询能力限定为“本地可追踪订单/成交”

M1 的 `query_order`、`query_trades`、`sync_today_trades` 只要求查询和恢复“由新主线提交并被本地事件流追踪到”的订单/成交。它们将基于 canonical store 的事件、订单快照、成交 fill 和结果对话框信息重建视图。

完整的券商委托页/成交页抓取、`sync_open_orders`、账户、持仓放到后续阶段。这样 M1 可以先建立统一主线，而不是被桌面抓取工程阻塞。

备选方案：
- 在 M1 直接承诺完整券商委托/成交查询
  - 被否决，因为当前仓库几乎没有现成查询页能力，风险和范围都过大

### 5. 新旧 CLI 并存，旧命令先转发或保留为边界命令

M1 新增：
- `trade order-place`
- `trade order-query`
- `trade trade-query`

同时保留：
- `trade buy`
- `trade submit-once`
- `trade submit-ready`
- `trade confirm-current`

其中：
- `trade buy` 作为兼容入口，最终等价于 `trade order-place --side buy`
- `trade submit-once` 作为兼容入口，最终等价于 `trade order-place` 的 PingAn 即时确认模式
- `trade submit-ready`、`trade confirm-current` 保留为 PingAn 专用边界命令，不提升为 canonical 统一接口

备选方案：
- 一次性替换旧命令
  - 被否决，因为会直接打断现有脚本与运维习惯

### 6. 新增 canonical 运行时存储，但保留现有 `pingan-*` 产物

系统将新增 `runtime/trader/` 目录，承载：
- `order-events.jsonl`
- `order-snapshots.jsonl`
- `trade-fills.jsonl`
- `latest-orders.json`
- `latest-trades.json`

迁移期内，现有 `pingan-last-order.json`、`pingan-order-events.jsonl`、`pingan-submission-ledger.jsonl`、`trade-audits/` 继续保留。新主线写 canonical store，兼容命令在必要时继续补写旧产物，直到报告和审计逐步迁出 `PingAn` 特化路径。

## Risks / Trade-offs

- [卖出链路目前不存在] → M1 需要新建卖出页激活、卖出按钮定位和结果文案验证；通过把“页面探测”和“提交流程”拆分为可复用桌面步骤来降低重复实现。
- [桌面券商不具备原生 push 回报] → 明确把回报能力设计为 synthetic event，避免对外承诺柜台级实时推送。
- [项目当前文档边界与新方向冲突] → 在 proposal/spec 阶段显式声明这是“新增证券交易主线”，并在后续文档变更中更新“非主线”表述。
- [新旧双轨入口会增加一段时间的复杂度] → 通过“新命令先新增、旧命令逐步转发”的迁移策略，把风险从一次性切换改成分阶段收口。
- [M1 查询能力比理想状态弱] → 明确限制为“本地可追踪订单/成交”，把券商委托页/成交页抓取留给 M2/M3。

## Migration Plan

1. 新增 `tdxquant/trader/` 领域层与 canonical store，但不改动现有生产命令行为。
2. 新增 broker-neutral CLI 命令 `trade order-place`、`trade order-query`、`trade trade-query`。
3. 引入 `PingAnDesktopTraderGateway`，先支持普通 A 股现货限价 `buy/sell`。
4. 让 `trade buy`、`trade submit-once` 逐步转发到 `TradeService`，同时保留 `trade submit-ready`、`trade confirm-current` 作为 PingAn 边界命令。
5. 在后续阶段扩展 `cancel_order`、`sync_open_orders`、账户、持仓和更完整的同步恢复能力。

回滚策略：
- 新主线和 canonical store 都是增量引入；若新命令或新主线存在问题，可以停用新命令并回退兼容转发，而不影响现有 `PingAn` 旧链路。

## Open Questions

- `broker` 的首批 canonical 标识是否统一使用 `pingan_desktop`，还是保持现有审计里更短的 `pingan`。
- M1 是否需要同步新增 task 层的 broker-neutral 封装，还是先只从 CLI 落地再向 task/cataloɡ 扩展。
- 卖出链路是否需要独立 profile 名称，还是与买入共用同一套桌面运行时 profile。
