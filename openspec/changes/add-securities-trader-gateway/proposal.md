## Why

当前桌面交易能力仍以 `PingAn` 买入提交流程为中心，缺少 broker-neutral 的证券交易主线，无法把生命周期、买卖对称下单、统一订单/成交查询与同步能力收口成稳定接口。现在补齐这条主线，可以在不打断现有平安桌面交易流程的前提下，为后续多券商扩展和更完整的证券交易治理建立标准边界。

## What Changes

- 新增并行的证券交易主线，定义 broker-neutral 的 `SecuritiesTraderGateway`、统一交易模型、生命周期状态机和规范化事件/快照持久化。
- 以 `PingAnDesktopTraderGateway` 作为第一号实现，支持普通 A 股现货限价 `buy/sell` 下单。
- 新增 broker-neutral 的交易入口，优先落地 `trade order-place`、`trade order-query`、`trade trade-query`。
- 保留现有 `trade buy`、`trade submit-once`、`trade submit-ready`、`trade confirm-current` 作为兼容入口，并逐步转发到新主线或保留为 PingAn 专用边界命令。
- M1 的 `query_order`、`query_trades`、`sync_today_trades` 先收口为“新网关本地可追踪订单/成交”的统一查询与恢复能力，不在首批范围内承诺完整的券商委托页/成交页抓取。

## Capabilities

### New Capabilities
- `tdx-securities-trader-gateway`: 定义 A 股证券交易统一网关、统一模型、生命周期状态机、事件/快照存储，以及基于 PingAn 桌面链路的第一号 broker 实现。

### Modified Capabilities
- `tdx-desktop-trading-cli-entry`: 交易 CLI 需要新增 broker-neutral 标准命令，同时保留现有 PingAn 命令作为兼容入口。
- `tdx-desktop-trading-management`: 桌面交易治理需要从单一 `TdxTradeManager.pingan.*` 路径扩展为并行的 `TradeService + TraderGateway` 主线，并保留旧管理层作为迁移兼容面。

## Impact

- 受影响代码将集中在新增 `tdxquant/trader/` 领域层，以及调整 [tdxquant/cli.py](/opt/iflow/TdxQuant/tdxquant/cli.py)、[tdxquant/trade/manager.py](/opt/iflow/TdxQuant/tdxquant/trade/manager.py) 和部分 `PingAn` 桌面交易编排路径。
- 运行时将新增 canonical 交易事件、订单快照和成交填报存储目录，现有 `pingan-*` 产物在迁移期内继续保留。
- 对外行为以新增命令和兼容转发为主，不引入立即破坏现有桌面交易命令的变更。
