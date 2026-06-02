# TdxQuant 数据能力清单

> 基于代码库 `tqcenter.py`、`tdxquant/api/`、`tdxdata_test.py` 整理，供交易审计系统数据源评估。

## 前提条件

| 条件 | 说明 |
|------|------|
| Windows 环境 | 所有数据调用依赖 `TPythClient.dll`，必须在原生 Windows Python 下运行 |
| TDX 客户端在线 | 需启动通达信金融终端并登录 |
| 盘后数据下载 | K线历史、交易日历等需在客户端"系统 → 盘后数据下载"中预先下载 |

---

## 一、历史 K 线数据（替代腾讯K线）

**接口**：`tq.get_market_data()`

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `stock_list` | `list[str]` | 股票代码，格式 `6位.市场`（如 `000001.SZ`、`600519.SH`） |
| `period` | `str` | **必填**。支持：`1m`, `5m`, `10m`, `15m`, `30m`, `1h`, `1d`, `1w`, `1mon`, `1q`, `1y` |
| `start_time` | `str` | 起始日期 `YYYYMMDD` 或 `YYYYMMDDHHMMSS`，空=无下界 |
| `end_time` | `str` | 结束日期，空=取到当前 |
| `count` | `int` | 返回根数，`-1`=取范围内全部（默认），正数=取最近N根 |
| `dividend_type` | `str` | `none`（不复权）、`front`（前复权）、`back`（后复权） |
| `field_list` | `list[str]` | 筛选字段，空=全部。可选：`Open`, `Close`, `High`, `Low`, `Volume`, `Amount` 等 |
| `fill_data` | `bool` | 是否填充缺失数据，默认 `True` |

### 返回字段与单位

| 字段 | 说明 | 单位 |
|------|------|------|
| Open | 开盘价 | 元 |
| High | 最高价 | 元 |
| Low | 最低价 | 元 |
| Close | 收盘价 | 元 |
| Volume | 成交量 | 手 |
| Amount | 成交额 | 万元 |

### 数据范围

- **时间跨度**：取决于客户端盘后数据下载范围，可覆盖 2015 年至今
- **单次请求限制**：无 620 根分批限制，`count=-1` 可一次取全部
- **超时**：DLL 调用 10 秒超时
- **支持标的**：A股（`.SH`/`.SZ`/`.BJ`）、指数（如 `999999.SH` 上证综指、`000300.SH` 沪深300）、中证指数（`.CSI`）、期货（`.CFF`）

### 指数数据（替代上证指数K线）

与个股 K 线使用同一接口，无需特殊 key 格式：

```python
# 上证综指日线
tq.get_market_data(stock_list=['999999.SH'], period='1d', start_time='20151001', dividend_type='front')
# 沪深300日线
tq.get_market_data(stock_list=['000300.SH'], period='1d', start_time='20151001', dividend_type='front')
```

### 与腾讯K线对比

| 对比项 | 腾讯K线 | TdxQuant |
|--------|---------|----------|
| 单次上限 | 620根，需分批 | 无硬限制，`count=-1` 全取 |
| 复权 | 需指定 `qfqday` | `dividend_type='front'` 参数控制 |
| 指数 | key 格式不同（`day` vs `qfqday`） | 统一接口，换 code 即可 |
| 网络依赖 | 需要 | 不需要（本地数据） |
| 超时风险 | 网络波动 | 10s DLL 超时 |
| 数据新鲜度 | 实时 | 需预下载或 `refresh_kline()` 刷新 |

---

## 二、实时行情数据（替代腾讯行情）

**接口**：`tq.get_full_tick()` / `tq.get_market_snapshot()`

### get_full_tick()

| 参数 | 类型 | 说明 |
|------|------|------|
| `stock_code` | `str` | 单个股票代码 |

返回当前快照（最新价、开盘、最高、最低、成交量、成交额、买卖五档等）。超时 50 秒。

### get_market_snapshot()（2026-02-28 新增）

| 参数 | 类型 | 说明 |
|------|------|------|
| `stock_code` | `str` | 股票代码 |
| `field_list` | `list[str]` | 字段筛选 |

### 实时订阅

`tq.subscribe_hq(stock_list, callback)` 推送式更新，最多同时订阅 **100 只**。

### 与腾讯行情对比

| 对比项 | 腾讯 qt.gtimg.cn | TdxQuant |
|--------|------------------|----------|
| 数据类型 | 仅当前价 | 快照+五档+推送 |
| 历史 | 不可取 | 不提供（用 K 线接口） |
| 延迟 | 网络延迟 | 本地 DLL 调用 |

---

## 三、交易日历

**接口**：`tq.get_trading_dates()`

| 参数 | 类型 | 说明 |
|------|------|------|
| `market` | `str` | 市场（如 `'SH'`） |
| `start_time` | `str` | 起始日期 |
| `end_time` | `str` | 结束日期 |
| `count` | `int` | 数量限制 |

**前提**：需下载上证指数（999999）盘后数据。目前仅支持 A 股。

---

## 四、股票列表

**接口**：`tq.get_stock_list(list_type)`

| list_type | 说明 |
|-----------|------|
| 0 | 自选股 |
| 1 | 持仓股 |
| 5 | 所有A股 |
| 6 | 上证指数成份股 |
| 7 | 上证主板 |
| 8 | 深证主板 |
| 9 | 重点指数 |
| 10 | 所有板块指数 |
| 11 | 缺省行业板块 |
| 12 | 概念板块 |
| 13 | 风格板块 |
| 14 | 地区板块 |
| 23 | 沪深300 |
| 24 | 中证500 |
| 25 | 中证1000 |
| 26 | 国证2000 |
| 27 | 中证2000 |
| 28 | 中证A500 |
| 31 | ETF基金 |
| 32 | 可转债 |
| 50 | 沪深A股 |
| 51 | 创业板 |
| 52 | 科创板 |
| 53 | 北交所 |
| 101 | 国内期货 |
| 102 | 港股 |
| 103 | 美股 |

---

## 五、基础财务数据

**接口**：`tq.get_stock_info(stock_code, field_list)`

返回股本、资产、负债、利润、现金流量等。股本/资产/负债/利润单位为**万元**。无需下载专业财务数据。

---

## 六、专业财务数据

**接口**：`tq.get_financial_data()` / `tq.get_financial_data_by_date()`

| 参数 | 说明 |
|------|------|
| `stock_list` | 股票代码列表 |
| `field_list` | 字段列表，格式 `FnXXX`（如 `Fn193`） |
| `start_time` / `end_time` | 日期范围 |
| `report_type` | `report_time`（截止日期）或 `announce_time`（公告日期） |

**前提**：需在客户端下载专业财务数据。超时 60 秒。

---

## 七、除权除息数据

**接口**：`tq.get_divid_factors(stock_code, start_time, end_time)`

返回分红送配记录。配合 K 线复权使用。

---

## 八、可转债数据

**接口**：`tq.get_cb_info(stock_code, field_list)`

返回可转债基础数据。

---

## 九、技术指标公式（可用于审计计算）

**接口**：`tq.formula_zb()`

直接调用通达信内置技术指标公式（MA、MACD、KDJ、BOLL 等），无需自行实现。

**相关接口**：
- `tq.formula_xg()` — 条件选股公式
- `tq.formula_exp()` — 专家系统公式
- `tq.formula_process_mul_zb()` — 批量指标计算
- `tq.formula_process_mul_xg()` — 批量选股

---

## 十、数据刷新与缓存

| 接口 | 说明 | 限制 |
|------|------|------|
| `tq.refresh_cache()` | 刷新行情缓存 | 5 分钟内不重复触发；可选 `force`、`market` 参数 |
| `tq.refresh_kline()` | 刷新 K 线缓存 | 仅支持 `1m`、`5m`、`1d`；不建议一次更新太多 |

---

## 限制汇总

| 限制项 | 详情 |
|--------|------|
| 运行平台 | 仅 Windows，依赖 TDX 客户端 DLL |
| 数据前提 | K线需预下载盘后数据，财务数据需下载专业财务数据 |
| 分笔数据 | 暂不支持（`tick` 周期不可用） |
| 实时订阅上限 | 最多 100 只 |
| 缓存刷新冷却 | 5 分钟 |
| DLL 超时 | K线 10s，快照 50s，财务 60s |
| 策略实例 | 同名策略不可同时运行 |

---

## 交易审计场景适用性

| 审计需求 | TdxQuant 能否满足 | 推荐接口 |
|----------|-------------------|----------|
| 入场日 K 线（OHLCV） | **可以** | `get_market_data(period='1d', dividend_type='front')` |
| 入场时大盘指数 | **可以** | `get_market_data(stock_list=['999999.SH'])` |
| 实时当前价 | **可以** | `get_full_tick()` 或 `get_market_snapshot()` |
| 技术指标（MA/MACD/KDJ） | **可以** | `formula_zb()` 内置计算 |
| 前复权价格 | **可以** | `dividend_type='front'` |
| 交易日判断 | **可以** | `get_trading_dates()` |
| 2015年10月前数据 | **取决于盘后下载范围** | 需确认客户端是否下载了对应历史数据 |
| 分笔成交 | **不可以** | 暂不支持 tick 数据 |
