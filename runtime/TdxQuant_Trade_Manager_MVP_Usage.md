# TdxQuant Trade Manager / Securities Trader M1 使用说明

## 目标

当前桌面交易能力已经拆成“两条并行主线”：

- 交易 manager：`tdxquant/trade/manager.py`
- 证券 trader：`tdxquant/trader/`
- 交易 profile：`runtime/trade-profiles.json`
- 交易 preset：`runtime/trade-presets.json`
- 交易上下文辅助：`tdxquant/trade/context.py`

M1 的证券 trader 主线只覆盖普通 A 股现货限价 `buy/sell` 与本地 tracked-order / trade query；底层仍复用现有 PingAn 桌面执行路径，不改 `desktop/uia.py` 的真实执行框架。

## 当前结构

- `TdxTradeManager`
  - 顶层桌面交易管理入口
  - 负责 profile 解析、manager metadata、状态文件回填、事件日志追加
- `TradeService`
  - broker-neutral 的证券交易编排入口
  - 负责 canonical 下单、订单查询、成交查询、同日成交恢复
- `PingAnDesktopTraderGateway`
  - 第一号证券 gateway 实现
  - 当前已接入 `side=buy` 与 `submit_once` 兼容执行模式
- `TraderStore`
  - canonical runtime 存储
  - 负责 `order-events` / `order-snapshots` / `trade-fills`
- `manager.pingan.buy(...)`
  - 对应稳定快速买入路径
  - 底层调用 `run_pingan_buy_fast(...)`
- `manager.pingan.buy_submit_once(...)`
  - 对应完整提交确认路径
  - 底层调用 `run_pingan_buy_submit_once(...)`

## 默认产物

- 最后一次订单状态：
  - `runtime/pingan-last-order.json`
- 追加事件日志：
  - `runtime/pingan-order-events.jsonl`

每次 `pingan-buy` 或 `pingan-buy-submit-once` 成功或失败后，manager 都会回填这两个文件。

新增 canonical trader 产物：

- `runtime/trader/order-events.jsonl`
- `runtime/trader/order-snapshots.jsonl`
- `runtime/trader/trade-fills.jsonl`
- `runtime/trader/latest-orders.json`
- `runtime/trader/latest-trades.json`

迁移边界：

- legacy `pingan-*` 产物继续保留，供现有审计和运维入口消费
- canonical `runtime/trader/*` 产物用于 broker-neutral 证券交易主线

## Python 用法

```python
from tdxquant import TdxTradeManager

manager = TdxTradeManager(
    profile="turbo",
    title_keyword="平安证券",
    exe_path=r"D:\ProgramData\PinganSec\TdxW.exe",
)

result = manager.pingan.buy(
    port="COM3",
    code="516820",
    price="0.35",
    quantity=100,
)
```

`result.data` 中会附带：

- `manager`
- `trade_profile`
- `timing`
- `artifacts.last_order_state_path`
- `artifacts.order_event_log_path`

## CLI 兼容关系

现有 flat 命令仍保持不变：

- `pingan-buy`
- `pingan-buy-submit-once`

现有 nested 兼容命令继续保留：

- `trade buy`
- `trade submit-once`
- `trade submit-ready`
- `trade confirm-current`

新增 broker-neutral 证券交易入口：

- `trade order-place`
- `trade order-query`
- `trade trade-query`
- `trade presets`
- `trade run --preset ...`

当前迁移关系是：

- `trade buy`：兼容入口，内部转发到 canonical `TradeService.place_order(... side=buy ...)`
- `trade submit-once`：兼容入口，内部转发到 canonical `TradeService.place_order(...)` 的 PingAn `submit_once` 执行模式
- `trade submit-ready` / `trade confirm-current`：继续保留为 PingAn 桌面边界命令
- profile 不再硬编码在 `cli.py`
- canonical 订单/成交快照落到 `runtime/trader/*`
- CLI 仍保留合同号 stderr 输出和最终 JSON 输出

## Broker-Neutral CLI 示例

```bash
python -m tdxquant.cli trade order-place \
  --broker pingan_desktop \
  --port COM3 \
  --market SZ \
  --side buy \
  --code 516820 \
  --price 0.35 \
  --quantity 100

python -m tdxquant.cli trade order-query --gateway-order-id <gateway_order_id>
python -m tdxquant.cli trade trade-query
```

首批边界：

- `trade order-place` 当前只接受普通 A 股现货限价单
- `trade order-query` / `trade trade-query` 当前只查询 canonical trader store 中的本地 tracked-order / trade
- 不承诺完整券商委托页 / 成交页抓取

## Trade Presets

如果你已经把常用环境参数固定下来，可以直接使用 trade preset：

```bash
python -m tdxquant.cli trade presets
python -m tdxquant.cli trade run --preset balanced-buy --code 516820 --price 0.35 --quantity 100
python -m tdxquant.cli trade run --preset turbo-buy --code 516820 --price 0.35 --quantity 100
python -m tdxquant.cli trade run --preset submit-once-default --code 516820 --price 0.35 --quantity 100
```

边界约定：

- `trade profile` 负责交易流程内部参数，例如延时、确认框等待和 Win32/UIA 输入策略。
- `trade preset` 负责命令级默认值，例如 `port`、`title_key`、`profile`、`max_depth`。
- preset 中定义的是默认参数；如果命令行显式再传一次同名参数，以命令行参数为准。
- 内置示例 preset 默认只固定环境参数，`code/price/quantity` 仍建议每次调用时显式输入。

## 后续建议

- 下一步优先补 `side=sell` 的 PingAn 桌面执行链路
- 再补 canonical `sync_today_trades` 的更完整恢复来源
- 后续阶段再扩展撤单、账户、持仓与更强的同步能力
