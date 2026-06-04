# TdxQuant 多数据源架构分析

> 生成日期: 2026-06-04
> 涉及项目: TdxQuant (Python), tdx-api (Go), pytdx (Python)

## 1. 三方对比

| 维度 | DLL (tqcenter) | pytdx | tdx-api Docker |
|------|---------------|-------|----------------|
| 平台 | Windows only | 全平台 | 全平台 (HTTP) |
| 部署 | 需安装通达信客户端 | pip install pytdx | docker-compose up |
| 连接管理 | DLL内部 | 需自己管理 | Go已实现(池化/选速/重连) |
| 性能 | 最快(内存调用) | 快(直连TCP) | 略慢(多一层HTTP) |
| 功能完整度 | 最全 | 基础数据 | 基础数据+扩展API |
| 适合场景 | Windows日常开发 | 轻量脚本/服务器 | 服务器7x24运行 |

## 2. DLL函数 vs pytdx 完整对照

### 2.1 pytdx可覆盖的函数 (9个核心查询)

| tqcenter方法 | DLL函数 | pytdx等价方法 | 覆盖度 |
|---|---|---|---|
| `get_market_data` | `GetHISDATsInStr` | `get_security_bars()` / `get_index_bars()` | 完全覆盖 |
| `get_full_tick` | `GetREPORTInStr` | `get_security_quotes()` | 完全覆盖 |
| `get_stock_list` | `GetStockListInStr` | `get_security_list()` + `get_security_count()` | 完全覆盖 |
| `get_sector_list` | `GetBlockListInStr` | `get_and_parse_block_info()` | 完全覆盖 |
| `get_stock_list_in_sector` | `GetBlockStocksInStr` | `get_and_parse_block_info()` | 基本覆盖 |
| `get_divid_factors` | `GetCWDATAInStr` | `get_xdxr_info()` | 完全覆盖 |
| `get_trading_dates` | `GetTradeCalendarInStr` | `pytdx.util.trade_date` | 本地缓存版 |
| `get_financial_data` | `GetProDataInStr(type=1)` | `get_finance_info()` + `HistoryFinancialCrawler` | 基本覆盖 |
| `get_market_snapshot` | `GetREPORTInStr` | `get_security_quotes()` | 完全覆盖 |

### 2.2 DLL独有函数 (38个, pytdx无法覆盖)

#### TDX客户端交互 (7个) — Docker环境不需要

| 函数 | 说明 |
|---|---|
| `send_message` | 向TDX客户端发送消息 |
| `send_file` | 向TDX客户端发送文件 |
| `send_warn` | 向TDX客户端发送预警 |
| `send_bt_data` | 向TDX客户端发送回测数据 |
| `send_user_block` | 向TDX客户端添加自选股 |
| `print_to_tdx` | 导出数据到TDX客户端 |
| `exec_to_tdx` | 执行TDX客户端命令 |

#### 公式引擎 (10个) — 可用ta-lib/pandas-ta替代

| 函数 | 说明 |
|---|---|
| `formula_format_data` | 格式化公式输入数据 |
| `formula_set_data` | 设置公式数据 |
| `formula_set_data_info` | 设置公式数据信息 |
| `formula_get_data` | 获取公式计算结果 |
| `formula_zb` | 执行指标公式 |
| `formula_xg` | 执行选股公式 |
| `formula_exp` | 执行专家公式 |
| `formula_process_mul_xg` | 批量选股公式 |
| `formula_process_mul_zb` | 批量指标公式 |
| `formula_screen` / `formula_get_all` / `formula_get_info` | 公式列表/详情 |

#### 实时订阅推送 (4个) — 可用轮询替代

| 函数 | 说明 |
|---|---|
| `subscribe_quote` | 订阅单股行情回调 |
| `subscribe_hq` | 订阅行情更新 |
| `unsubscribe_hq` | 取消订阅 |
| `get_subscribe_hq_stock_list` | 获取已订阅列表 |

#### 专业数据 ProData (7个) — 需第三方数据源补充

| 函数 | 说明 |
|---|---|
| `get_gpjy_value` | 股票交易数据(资金流向) |
| `get_gpjy_value_by_date` | 按日期股票交易数据 |
| `get_bkjy_value` | 板块交易数据 |
| `get_bkjy_value_by_date` | 按日期板块交易数据 |
| `get_scjy_value` | 市场交易数据 |
| `get_scjy_value_by_date` | 按日期市场交易数据 |
| `get_gp_one_data` | 股票单点数据 |

#### 板块写操作 (4个) — 仅DLL

| 函数 | 说明 |
|---|---|
| `create_sector` | 创建自定义板块 |
| `delete_sector` | 删除自定义板块 |
| `rename_sector` | 重命名自定义板块 |
| `clear_sector` | 清空自定义板块 |

#### 交易接口 (6个) — 可用券商API替代

| 函数 | 说明 |
|---|---|
| `order_stock` | 下单 |
| `stock_account` | 获取账户 |
| `query_stock_orders` | 查询委托 |
| `query_stock_positions` | 查询持仓 |
| `cancel_order_stock` | 撤单 |
| `query_stock_asset` | 查询资产 |

#### 特殊信息 (6个) — DLL特有

| 函数 | 说明 |
|---|---|
| `get_cb_info` | 可转债基础信息 |
| `get_ipo_info` | 新股申购信息 |
| `get_more_info` | 更多股票信息 |
| `get_relation` | 关联数据 |
| `get_trackzs_etf_info` | ETF跟踪指数信息 |
| `get_gb_info` / `gb_info_by_date` | 股本信息 |

## 3. 架构设计

### 3.1 数据源优先级

```
Windows桌面:  DLL(主) → pytdx(辅) → tdx-api HTTP(兜底)
Docker服务器: pytdx(主) → tdx-api HTTP(辅)
轻量脚本:     pytdx(唯一)
```

### 3.2 调用链

```
bridge.py run_tdx_*()
    │
    ├── _run_tq_call()          [DLL路径, Windows only, 不变]
    │
    ├── _run_pytdx_call()       [pytdx路径, 全平台, 新增]
    │
    └── _run_dispatch()         [新增调度层]
            → 检测provider可用性
            → 按优先级选择
            → 自动fallback
```

### 3.3 覆盖策略

| 函数类别 | DLL | pytdx | Docker环境处理 |
|----------|-----|-------|---------------|
| 行情/K线/分时 | 优先 | 备选 | pytdx覆盖 |
| 股票/板块列表 | 优先 | 备选 | pytdx覆盖 |
| 财务/除权 | 优先 | 备选 | pytdx覆盖 |
| 公式引擎 | 唯一 | — | 返回UNSUPPORTED + 建议ta-lib |
| 实时订阅 | 唯一 | — | 轮询模式替代 |
| 专业ProData | 唯一 | — | 返回UNSUPPORTED |
| 板块写操作 | 唯一 | — | 返回UNSUPPORTED |
| 交易 | 唯一 | — | 返回UNSUPPORTED |
| 客户端交互 | 唯一 | — | 返回UNSUPPORTED(不需要) |

## 4. 实现计划

### Phase 1: pytdx Provider核心 (P0)

- 创建 `provider_pytdx.py` 实现9个核心函数的pytdx等价
- 连接管理(connect/disconnect/reconnect)
- 代码格式转换(600000.SH → market=1, code='600000')

### Phase 2: Bridge调度层 (P0)

- 修改 `bridge.py` 添加 `_run_dispatch()`
- 运行时自动探测provider可用性
- DLL优先 + pytdx fallback

### Phase 3: tdx-api HTTP Provider (P1)

- 创建 `provider_tdxapi.py` 通过HTTP调用tdx-api Docker容器
- 复用tdx-api的REST API

### Phase 4: Docker化 (P2)

- Python项目Dockerfile
- docker-compose编排
- 健康检查

## 5. pytdx API速查

### 连接

```python
from pytdx.hq import TdxHq_API
api = TdxHq_API()
api.connect('119.147.212.81', 7709)  # 返回True/False
api.disconnect()
```

### K线

```python
# category: 0=5min, 1=15min, 2=30min, 3=1h, 4=day, 5=week, 6=month, 8=1min
# market: 0=SZ, 1=SH
df = api.to_df(api.get_security_bars(4, 1, '600000', 0, 800))
# 返回: open, close, high, low, vol, amount, datetime
```

### 行情

```python
quotes = api.get_security_quotes([(1, '600000'), (0, '000001')])
# 返回: price, open, high, low, bid1-5, ask1-5, vol, amount 等
```

### 除权除息

```python
xdxr = api.get_xdxr_info(1, '600000')
# 返回: fenhong, songzhuangu, peigu, peigujia 等
```

### 财务

```python
finance = api.get_finance_info(1, '600000')
# 返回: liutongguben, zongguben, zongzichan, jinglirun 等
```

### 股票列表

```python
count = api.get_security_count(1)  # 上海市场证券总数
stocks = api.get_security_list(1, 0)  # 从位置0开始
# 返回: code, name, pre_close, decimal_point
```

### 板块

```python
blocks = api.get_and_parse_block_info('block_gn.dat')  # 行业板块
# 返回: blockname, block_type, code_index, code
```

### 交易日历

```python
from pytdx.util.trade_date import trade_date_sse
dates = trade_date_sse  # numpy array of trade dates
```
