# 开发总结：17 个 API 函数全量实现

## 概述

对照 web_docs 官方文档（`docs/web_docs/`）与现有代码，识别出 17 个缺失的 API 函数，按 5 层架构（bridge → domain API → manager proxy → capability registry → CLI）全量补齐。所有 469 个已有测试通过，无回归。

## 缺口分析

### Group A — 桥接已有 tqcenter DLL（3 个）

这些函数在 `tqcenter.py` 中已有 DLL 实现，但未接入 bridge 层。

| 函数 | tqcenter.py 位置 | 用途 |
|---|---|---|
| `send_message` | L1287 `dll.SetResToMain` MSG\|\| | 发消息到 TQ 策略界面 |
| `send_file` | L1314 FILE\|\| | 发文件到客户端数据浏览 |
| `send_bt_data` | L1393 BTR\|\| | 发回测数据到客户端 |

### Group B — 仅文档记载，tqcenter 尚未实现（8 个）

使用 `_require_tq_method` 前向兼容策略：DLL 实现前调用会抛出 `RuntimeError`，实现后自动生效。

| 函数 | 所属域 | 文档来源 |
|---|---|---|
| `get_relation` | meta | 调用通达信公式 |
| `gb_info_by_date` | meta | 调用通达信公式 |
| `get_pricevol` | market | 行情类信息 |
| `get_trackzs_etf_info` | market | ETF可转债期货数据 |
| `formula_get_all` | formula | 调用通达信公式 |
| `formula_get_info` | formula | 调用通达信公式 |
| `print_to_tdx` | runtime | 通用函数 |
| `exec_to_tdx` | runtime | 通用函数 |

### Group C — 交易域（6 个）

新建 `trade_api.py` 域类，与现有 PingAn 桌面自动化交易（Section D）平行共存。

| 函数 | 用途 |
|---|---|
| `stock_account` | 获取资金账户句柄 |
| `order_stock` | 买卖下单 |
| `query_stock_orders` | 查询今日委托 |
| `query_stock_positions` | 查询持仓 |
| `cancel_order_stock` | 撤单 |
| `query_stock_asset` | 查询账户资产 |

## 修改的文件

| 文件 | 变更 |
|---|---|
| `tdxquant/api/bridge.py` | 新增 17 个 `run_tdx_*` 桥接函数 |
| `tdxquant/api/runtime.py` | 新增 5 个方法 + 5 个 import |
| `tdxquant/api/market.py` | 新增 2 个方法 + 2 个 import |
| `tdxquant/api/meta.py` | 新增 2 个方法 + 2 个 import |
| `tdxquant/api/formula.py` | 新增 2 个方法 + 2 个 import |
| `tdxquant/api/trade_api.py` | **新建** TradeApi 类（6 个方法） |
| `tdxquant/api/manager.py` | 新增 `_TradeApiManagerProxy`（6 个方法）；`_RuntimeManagerProxy` +5、`_MarketManagerProxy` +2、`_MetaManagerProxy` +2、`_FormulaManagerProxy` +2；`TdxApiManager` 新增 `_trade_api` / `trade` |
| `tdxquant/provider_discovery.py` | 新增 17 个 `_capability(...)` 条目（55 → 72） |
| `tdxquant/cli.py` | 新增 17 个 parser block + 17 个 dispatch block |
| `FUNCTION_TREE.md` | 新增 E-14 条目 |

## 用户使用方式

### Python API

```python
from tdxquant.api import TdxApiManager

m = TdxApiManager(strategy_path=".")

# Group A — 客户端交互
m.runtime.send_message("策略启动")
m.runtime.send_file("report.txt")
m.runtime.send_bt_data("688318.SH", ["20251215141115"], [["11"]], count=1)

# Group B — 查询（需 tqcenter DLL 支持）
m.meta.get_relation(stock_code="688318.SH", relation_type=1)
m.meta.gb_info_by_date(stock_code="688318.SH", date="20241231")
m.market.get_pricevol(stock_code="688318.SH", period="1d")
m.market.get_trackzs_etf_info(stock_code="159109.SH")
m.formula.get_all()
m.formula.get_info(formula_name="MACD")
m.runtime.print_to_tdx(df_list=[...], xml_filename="panel.xml")
m.runtime.exec_to_tdx(url="http://www.treeid/MAINQH")

# Group C — 交易（需 tqcenter DLL 支持）
handle = m.trade.stock_account(account="1190008847", account_type="stock")
m.trade.order_stock(account_id=handle, stock_code="688318.SH", order_type=0, order_volume=200, price_type=0, price=160.0)
m.trade.query_stock_orders(account_id=handle)
m.trade.query_stock_positions(account_id=handle)
m.trade.cancel_order_stock(account_id=handle, stock_code="688318.SH", order_id="48957")
m.trade.query_stock_asset(account_id=handle)
```

### CLI

```bash
python -m tdxquant api send-message --msg "hello"
python -m tdxquant api send-file --file report.txt
python -m tdxquant api send-bt-data --code 688318.SH --time 20251215141115 --data 11
python -m tdxquant api get-relation --code 688318.SH --relation-type 1
python -m tdxquant api gb-info-by-date --code 688318.SH --date 20241231
python -m tdxquant api get-pricevol --code 688318.SH --period 1d
python -m tdxquant api get-trackzs-etf-info --code 159109.SH
python -m tdxquant api formula-get-all
python -m tdxquant api formula-get-info --formula-name MACD
python -m tdxquant api print-to-tdx --input-json-file payload.json
python -m tdxquant api exec-to-tdx --url "http://www.treeid/MAINQH"
python -m tdxquant api stock-account --account 1190008847 --account-type stock
python -m tdxquant api order-stock --account-id 1 --code 688318.SH --order-type 0 --order-volume 200 --price-type 0 --price 160.0
python -m tdxquant api query-stock-orders --account-id 1 --code ""
python -m tdxquant api query-stock-positions --account-id 1
python -m tdxquant api cancel-order-stock --account-id 1 --code 688318.SH --order-id 48957
python -m tdxquant api query-stock-asset --account-id 1
```

## 验证结果

| 检查项 | 结果 |
|---|---|
| TradeApi import | OK |
| TdxApiManager.trade 属性 | 存在 |
| runtime 新方法可见 | send_message, send_file, send_bt_data, print_to_tdx, exec_to_tdx |
| market 新方法可见 | get_pricevol, get_trackzs_etf_info |
| meta 新方法可见 | get_relation, gb_info_by_date |
| formula 新方法可见 | get_all, get_info |
| trade 新方法可见 | stock_account, order_stock, query_stock_orders, query_stock_positions, cancel_order_stock, query_stock_asset |
| capability 总数 | 72（原 55 + 新 17） |
| CLI send-message --help | 正常解析 |
| CLI order-stock --help | 正常解析 |
| CLI get-pricevol --help | 正常解析 |
| 已有测试 | 469 passed, 0 failed |

## 前置条件说明

| 分组 | 前置条件 |
|---|---|
| Group A | 需通达信客户端运行 + tqcenter DLL 可加载（已有 DLL 实现） |
| Group B | 需 tqcenter 后续版本实现对应方法（当前调用会抛 RuntimeError） |
| Group C | 需 tqcenter 后续版本实现对应方法 + 客户端登录交易账户 |

## 架构说明

```
用户代码
  ↓
manager.runtime.send_message(...)     ← L3: 计时、元数据、profile、replay
  ↓
RuntimeApi.send_message(...)          ← L2: 薄包装，绑定 strategy_path
  ↓
bridge.run_tdx_send_message(...)      ← L1: 加载 tqcenter DLL，调用 send_message
  ↓
tqcenter.py → dll.SetResToMain(...)   ← L0: Windows 原生 DLL
```

PingAn 桌面自动化交易主线（Section D）完全不受影响，作为独立平行路径保留。
