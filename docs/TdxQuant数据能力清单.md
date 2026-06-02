# TdxQuant 数据能力清单

> 基于代码库分析 + 实际测试结果整理，供交易审计系统数据源评估。
> 测试环境：Windows TDX客户端 `D:\mystocks\tdx\tdx-quant\tdxw.exe`，Python 3.13，从 WSL 远程调用。

## 前提条件

| 条件 | 说明 | 状态 |
|------|------|------|
| Windows 环境 | 所有数据调用依赖 `TPythClient.dll`，必须在原生 Windows Python 下运行 | 已确认 |
| TDX 客户端在线 | 需启动通达信金融终端并登录 | 已确认在线 |
| 盘后数据下载 | K线历史、交易日历等需在客户端"系统 → 盘后数据下载"中预先下载 | 沪深京日线已下载至 2015 年 |
| WSL 调用方式 | 通过 `/mnt/c/.../python.exe script.py` 直接调用 Windows Python | 已验证可行 |

---

## 实测结果总览

| # | 能力 | 接口 | 测试结果 | 备注 |
|---|------|------|----------|------|
| 1 | 日线 K 线（前复权） | `get_market_data(period='1d')` | **PASS** | 返回 Close/Open/High/Low/Volume/Amount/ForwardFactor/VolInStock |
| 2 | 指数 K 线（上证综指） | `get_market_data(['999999.SH'])` | **PASS** | 同一接口，无特殊 key |
| 3 | 实时行情快照 | `get_market_snapshot()` | **PASS** | 含最新价、五档、均价等 30+ 字段 |
| 4 | 交易日历 | `get_trading_dates()` | **PASS** | 返回日期列表 |
| 5 | 股票列表（沪深A股） | `get_stock_list('50')` | **PASS** | 5209 只；北交所 320 只（type=53） |
| 6 | 基础财务数据 | `get_stock_info()` | **PASS** | 63 个字段，含行业分类 |
| 7 | 除权除息 | `get_divid_factors()` | **PASS** | 含 Type/Bonus/AllotPrice/ShareBonus/Allotment |
| 8 | 历史深度 2015-10 | `get_market_data(start='20151001')` | **PASS** | 17 bars，日线已覆盖至 2015 年 |
| 9 | 历史深度 2015-01 | `get_market_data(start='20150101')` | **PASS** | 20 bars |
| 10 | 历史深度 2010-01 | `get_market_data(start='20100101')` | **NO DATA** | 未下载至 2010 年，审计不需要 |
| 11 | 多股票同时取 | `get_market_data(stock_list=[...3只])` | **PASS** | 支持批量 |
| 12 | 北交所股票 | `get_stock_list('53')` + K线 | **PASS** | 920xxx.BJ 格式正常，K线可取 |
| 13 | 板块列表 | `get_sector_list()` | **PASS** | 586 个板块代码 |
| 14 | 板块指数K线 | `get_market_data(['880001.SH'])` | **PASS** | 板块指数可当股票一样取K线算涨跌 |
| 15 | 周线 K 线 | `get_market_data(period='1w')` | **PASS** | 22 bars |
| 16 | 技术指标 MA | `formula_zb('MA', '5,10,20,60')` | **PASS** | 返回 MA1~MA4（对应参数顺序） |
| 17 | 技术指标 MACD | `formula_zb('MACD', '12,26,9')` | **PASS** | 返回 DIF/DEA/MACD |
| 18 | 技术指标 BOLL | `formula_zb('BOLL', '20,2')` | **PASS** | 返回 BOLL(中轨)/UB(上轨)/LB(下轨) |
| 19 | 技术指标 ATR | `formula_zb('ATR', '14')` | **PASS** | 返回 ATR/MTR |
| 20 | 技术指标 RSI | `formula_zb('RSI', '6')` | **PASS** | 返回 RSI1(6)/RSI2(12)/RSI3(24) |
| 21 | 专业财务数据(范围) | `get_financial_data()` | **PASS** | 8行×7列，含 Fn001-Fn005 + announce_time + tag_time |
| 22 | 专业财务数据(按日) | `get_financial_data_by_date()` | **PASS** | 返回 dict 如 `{'FN001':'2.15'}` |
| 23 | 股票交易数据 | `get_gpjy_value()` | **PASS** | 接口可用，具体 GP 字段需查文档 |
| 24 | 股票交易数据(按日) | `get_gpjy_value_by_date()` | **PASS** | 返回 dict，部分值可能为 `'--'` |
| 25 | 市场交易数据 | `get_scjy_value()` | **PASS** | 接口可用 |
| 26 | 市场交易数据(按日) | `get_scjy_value_by_date()` | **PASS** | 返回 dict，部分值可能为 `'--'` |
| 27 | 更多行情信息 | `get_more_info()` | **PASS** | 88 个字段，含 MA5/ZAFPre5~60/PE/PB 等 |
| 28 | 可转债信息 | `get_kzz_info()` | **PASS** | 接口可用 |
| 29 | 5 分钟 K 线 | `get_market_data(period='5m')` | **NO DATA** | 分钟线下载中，未生效 |

---

## 一、历史 K 线数据（替代腾讯K线）

**接口**：`tq.get_market_data()`

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `stock_list` | `list[str]` | 股票代码，格式 `6位.市场`（`.SH`/`.SZ`/`.BJ`） |
| `period` | `str` | **必填**。支持：`1m`, `5m`, `10m`, `15m`, `30m`, `1h`, `1d`, `1w`, `1mon`, `1q`, `1y` |
| `start_time` | `str` | 起始日期 `YYYYMMDD` 或 `YYYYMMDDHHMMSS`，空=无下界 |
| `end_time` | `str` | 结束日期，空=取到当前 |
| `count` | `int` | 返回根数，`-1`=取范围内全部（默认），正数=取最近N根 |
| `dividend_type` | `str` | `none`（不复权）、`front`（前复权）、`back`（后复权） |
| `field_list` | `list[str]` | 筛选字段，空=全部 |
| `fill_data` | `bool` | 是否填充缺失数据，默认 `True` |

### 返回字段与单位（实测确认）

| 字段 | 说明 | 单位 |
|------|------|------|
| Open | 开盘价 | 元 |
| High | 最高价 | 元 |
| Low | 最低价 | 元 |
| Close | 收盘价 | 元 |
| Volume | 成交量 | **股**（非手，实测 000001.SZ 日均 ~1亿股） |
| Amount | 成交额 | 万元 |
| ForwardFactor | 前复权因子 | — |
| VolInStock | 股票成交量 | — |

> **注意**：文档说 Volume 单位为"手"，实测为"股"。使用时需注意换算。

### 数据范围（实测确认）

| 时段 | 000001.SZ | 999999.SH（上证综指） | 说明 |
|------|-----------|---------------------|------|
| 2015-10 | **OK** 17 bars | **OK** 17 bars | 审计起始点已覆盖 |
| 2015-01 | **OK** 20 bars | — | — |
| 2010-01 | NO DATA | — | 未下载至 2010 年，审计不需要 |
| 近期至当天 | **OK** | **OK** | 需 `refresh_kline()` 刷新当日 |

- **单次请求限制**：无 620 根分批限制，`count=-1` 可一次取全部
- **多股票同时**：支持一次传入多只股票代码，同时返回
- **北交所**：920xxx.BJ 格式已验证，K线可取

### 指数数据（替代上证指数K线）

与个股使用同一接口，无需特殊 key 格式。实测通过：

```python
# 上证综指 - 已验证
tq.get_market_data(stock_list=['999999.SH'], period='1d', start_time='20151001', dividend_type='none')
# 沪深300
tq.get_market_data(stock_list=['000300.SH'], period='1d', start_time='20151001', dividend_type='front')
```

### 板块指数（替代行业涨跌API）

板块指数代码通过 `get_sector_list()` 获取，K线取法与个股相同：

```python
# 已验证：880001.SH 板块指数正常返回 19 bars
tq.get_market_data(stock_list=['880001.SH'], period='1d', start_time='20250501', dividend_type='none')
```

**结论**：`get_sector_list()` 拿代码列表 → `get_market_data()` 批量取 K 线 → 算涨跌幅排名。不需要保留外部行业 API。

### 与腾讯K线对比

| 对比项 | 腾讯K线 | TdxQuant |
|--------|---------|----------|
| 单次上限 | 620根，需分批 | 无硬限制，`count=-1` 全取 |
| 复权 | 需指定 `qfqday` | `dividend_type='front'` 参数控制 |
| 指数 | key 格式不同（`day` vs `qfqday`） | 统一接口，换 code 即可 |
| 板块涨跌 | 需另调行业 API | 同一接口取板块指数 K 线 |
| 网络依赖 | 需要 | 不需要（本地数据） |
| 超时风险 | 网络波动 | 10s DLL 超时 |
| 数据新鲜度 | 实时 | 需预下载或 `refresh_kline()` 刷新 |
| 历史深度 | 腾讯服务器端覆盖完整 | 取决于盘后数据下载范围（当前 2015~至今） |

---

## 二、实时行情数据（替代腾讯行情）

### get_market_snapshot()（实测通过）

| 参数 | 类型 | 说明 |
|------|------|------|
| `stock_code` | `str` | 股票代码 |
| `field_list` | `list[str]` | 字段筛选，空=全部 |

**实测返回字段（000001.SZ）**：

| 字段 | 示例值 | 说明 |
|------|--------|------|
| Now | 11.08 | 最新价 |
| Open | 10.98 | 开盘价 |
| Max | 11.10 | 最高价 |
| Min | 10.94 | 最低价 |
| LastClose | 10.99 | 昨收价 |
| Volume | 885428 | 成交量（手） |
| Amount | 97815.94 | 成交额（万元） |
| Average | 11.05 | 均价 |
| Buyp | ['11.07',...] | 买五价 |
| Buyv | ['2662',...] | 买五量 |
| Sellp | ['11.08',...] | 卖五价 |
| Sellv | ['9485',...] | 卖五量 |
| Inside | 433543 | 内盘 |
| Outside | 451885 | 外盘 |

> **注意**：Windows 端 tqcenter 使用 `get_market_snapshot()` 而非 `get_full_tick()`（后者仅存在于 WSL 侧代码库）。

### 实时订阅

`tq.subscribe_hq(stock_list, callback)` 推送式更新，最多同时订阅 **100 只**。

---

## 三、交易日历（实测通过）

**接口**：`tq.get_trading_dates()`

| 参数 | 类型 | 说明 |
|------|------|------|
| `market` | `str` | 市场（如 `'SH'`） |
| `start_time` | `str` | 起始日期 |
| `end_time` | `str` | 结束日期 |
| `count` | `int` | 数量限制 |

**前提**：需下载上证指数（999999）盘后数据。仅支持 A 股。

---

## 四、股票列表（实测通过）

**接口**：`tq.get_stock_list(list_type)`

**实测**：`get_stock_list('50')` 返回 5209 只沪深A股，`get_stock_list('53')` 返回 320 只北交所。

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
| 23 | 沪深300 |
| 24 | 中证500 |
| 25 | 中证1000 |
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

## 五、基础财务数据（实测通过）

**接口**：`tq.get_stock_info(stock_code, field_list)`

**实测**：`get_stock_info('000001.SZ')` 返回 63 个字段，包含行业分类、股本、资产、负债、利润、现金流量等。

---

## 六、专业财务数据（实测通过）

### get_financial_data() — 对应通达信 FINVALUE

| 参数 | 说明 |
|------|------|
| `stock_list` | 股票代码列表 |
| `field_list` | 字段列表，格式 `FnXXX`（如 `Fn001`, `Fn193`） |
| `start_time` / `end_time` | 日期范围 |
| `report_type` | `report_time`（截止日期）或 `announce_time`（公告日期） |

**实测**：`get_financial_data(['000001.SZ'], ['Fn001','Fn002','Fn003','Fn004','Fn005'], start_time='20240101')` 返回 DataFrame（8行×7列），含 FN001~FN005 + announce_time + tag_time。

### get_financial_data_by_date() — 对应通达信 FINONE

| 参数 | 说明 |
|------|------|
| `stock_list` | 股票代码列表 |
| `field_list` | 字段列表 |
| `year` | 年份，0=最近 |
| `mmdd` | 月日，如 `1231`，0=最近 |

**实测**：`get_financial_data_by_date(['000001.SZ'], ['Fn001','Fn002','Fn003'], year=2024, mmdd=1231)` 返回 `{'FN001':'2.15', 'FN002':'2.16', 'FN003':'12.55'}`。

---

## 七、除权除息数据（实测通过）

**接口**：`tq.get_divid_factors(stock_code, start_time, end_time)`

**实测**：`get_divid_factors('000001.SZ', '20240101', '20251231')` 返回 DataFrame（4行），含 Date/Type/Bonus/AllotPrice/ShareBonus/Allotment。

---

## 八、股票/市场交易数据（实测通过）

### get_gpjy_value() — 对应通达信 GPJYVALUE

按日期范围查询股票交易数据。`field_list` 使用 `GP1`~`GPn` 格式。

### get_gpjy_value_by_date() — 对应通达信 GPJYONE

按指定年月日查询，返回 dict，部分值可能为 `'--'`（无数据）。

### get_scjy_value() — 对应通达信 SCJYVALUE

按日期范围查询市场整体交易数据（无需指定股票代码）。

### get_scjy_value_by_date() — 对应通达信 SCJYONE

按指定年月日查询，`field_list` 使用 `SC1`~`SCn` 格式。

---

## 九、技术指标公式（实测通过）

### 调用流程

```python
# Step 1: 设置数据（用日期范围或 count）
tq.formula_set_data_info(
    stock_code='000001.SZ',
    stock_period='1d',
    start_time='20250401',
    end_time='20250531',
    dividend_type=1  # 0=不复权, 1=前复权, 2=后复权
)

# Step 2: 调用公式
result = tq.formula_zb(formula_name='MACD', formula_arg='12,26,9', xsflag=6)
```

返回格式为 `dict`，key 为 `Value.指标名`，value 为 `list[str]`。`xsflag` 控制小数位数。

### 已验证指标

| 指标 | formula_name | formula_arg | 返回字段 | 用途 |
|------|-------------|-------------|---------|------|
| MA | `MA` | `'5,10,20,60'` | `Value.MA1`~`Value.MA4` | MA 排列判定 |
| MACD | `MACD` | `'12,26,9'` | `Value.DIF`, `Value.DEA`, `Value.MACD` | 金叉/死叉判定 |
| BOLL | `BOLL` | `'20,2'` | `Value.BOLL`(中轨), `Value.UB`(上轨), `Value.LB`(下轨) | BOLL 位置/开口 |
| ATR | `ATR` | `'14'` | `Value.ATR`, `Value.MTR` | ATR 止损价 |
| RSI | `RSI` | `'6'` | `Value.RSI1`(6), `Value.RSI2`(12), `Value.RSI3`(24) | 超买超卖 |
| KDJ | `KDJ` | `'9,3,3'` | 待验证 | 备用 |

**关键说明**：
- 每次调用 `formula_zb()` 前，必须先通过 `formula_set_data_info()` 或 `formula_set_data()` 设置数据
- 返回的 list 长度 = 设置的 K 线根数 - 指标预热期（如 MA60 需至少 60 根数据才返回有效值，前面为 None）
- `formula_arg` 中数字为逗号分隔，最多 16 个参数
- `xsflag` 参数控制返回值小数位数（`-1`=默认，`6`=6位小数）

### 其他公式接口

- `tq.formula_xg()` — 条件选股公式
- `tq.formula_exp()` — 专家系统公式
- `tq.formula_process_mul_zb()` — 批量指标计算
- `tq.formula_process_mul_xg()` — 批量选股

### EXTERNSTR/EXTERNVALUE/SIGNALS_SYS 说明

这三个是通达信公式内部的辅助函数，**不能**通过 `formula_zb()` 直接作为公式名调用。如需使用，需要在 TDX 客户端中创建自定义公式引用它们。不过这些函数的功能已被 Python API 覆盖（行业分类→`get_stock_info()`，板块涨跌→`get_market_data()` 取板块指数K线，财务数据→`get_financial_data()`）。

---

## 十、更多行情信息（实测通过）

**接口**：`tq.get_more_info(stock_code, field_list)`

**实测**：`get_more_info('000001.SZ')` 返回 88 个字段。关键字段：

| 字段 | 示例值 | 说明 |
|------|--------|------|
| MA5Value | 10.88 | MA5 值 |
| ZAFPre5 | 2.68 | 5日涨幅% |
| ZAFPre10 | 2.03 | 10日涨幅% |
| ZAFPre20 | -3.57 | 20日涨幅% |
| ZAFPre60 | 3.45 | 60日涨幅% |
| ZAFYesterday | 0.55 | 昨日涨幅% |
| StaticPE_TTM | 4.95 | 静态市盈率(TTM) |
| DynaPE | 3.70 | 动态市盈率 |
| PB_MRQ | 0.46 | 市净率 |
| DYRatio | 5.42 | 股息率 |
| Ltsz | 2150.14 | 流通市值（亿） |
| HisHigh | 13.09 | 历史最高 |
| HisLow | 10.43 | 历史最低 |
| ZTPrice | 12.09 | 涨停价 |
| DTPrice | 9.89 | 跌停价 |
| IPO_Price | 40.00 | 发行价 |
| BetaValue | 0.16 | Beta 值 |
| StaffNum | 41698 | 员工数 |
| FreeLtgb | 816048.13 | 流通股本（万股） |

---

## 十一、数据刷新与缓存

| 接口 | 说明 | 限制 |
|------|------|------|
| `tq.refresh_cache()` | 刷新行情缓存 | 5 分钟内不重复触发；可选 `force`、`market` 参数 |
| `tq.refresh_kline()` | 刷新 K 线缓存 | 仅支持 `1m`、`5m`、`1d`；不建议一次更新太多 |

当日数据取最新时需先刷新。盘中实时用 `get_market_snapshot()` 不需要刷新。

---

## 限制汇总

| 限制项 | 详情 | 影响程度 |
|--------|------|----------|
| 运行平台 | 仅 Windows，依赖 TDX 客户端 DLL | 已通过 WSL→Windows 调用解决 |
| **分钟线下载中** | 5m/15m/30m/1h/1m 当前全部 NO DATA | 中等：审计主要用日线，分钟线为增强功能 |
| 2010 年前数据 | 未下载，审计不需要 | 低 |
| 分笔数据 | 暂不支持 tick | 低：审计不需要 |
| 实时订阅上限 | 最多 100 只 | 低：审计为离线批量 |
| 缓存刷新冷却 | 5 分钟 | 低 |
| Volume 单位 | 实测为"股"而非文档说的"手" | 需注意换算 |

---

## 交易审计场景适用性

| 审计需求 | TdxQuant 能否满足 | 推荐接口 | 状态 |
|----------|-------------------|----------|------|
| 入场日 K 线（OHLCV） | **可以** | `get_market_data(period='1d', dividend_type='front')` | **已验证** |
| 入场时大盘指数 | **可以** | `get_market_data(['999999.SH'])` | **已验证** |
| 实时当前价 | **可以** | `get_market_snapshot()` | **已验证** |
| MA 排列判定 | **可以** | `formula_zb('MA', '5,10,20,60')` | **已验证** |
| MACD 金叉/死叉 | **可以** | `formula_zb('MACD', '12,26,9')` | **已验证** |
| BOLL 位置/开口 | **可以** | `formula_zb('BOLL', '20,2')` | **已验证** |
| ATR 止损价 | **可以** | `formula_zb('ATR', '14')` | **已验证** |
| RSI 超买超卖 | **可以** | `formula_zb('RSI', '6')` | **已验证** |
| 前复权价格 | **可以** | `dividend_type='front'` | **已验证** |
| 交易日判断 | **可以** | `get_trading_dates()` | **已验证** |
| 行业涨跌排名 | **可以** | `get_sector_list()` + `get_market_data()` 取板块K线 | **已验证** |
| 北交所股票 | **可以** | 920xxx.BJ 格式 | **已验证** |
| 2015年至今日线 | **可以** | 已下载覆盖 | **已验证** |
| 财务数据 | **可以** | `get_financial_data()` / `get_financial_data_by_date()` | **已验证** |
| 分钟线（入场时间精度） | **待生效** | `get_market_data(period='5m')` | 分钟线下载中 |
| 分笔成交 | **不可以** | — | 不支持 tick |

---

## 通达信函数 ↔ Python API 对照表

| 通达信公式函数 | Python API | 说明 |
|--------------|-----------|------|
| FINVALUE | `get_financial_data()` | 按范围取专业财务数据 |
| FINONE | `get_financial_data_by_date()` | 按日期取专业财务数据 |
| GPJYVALUE | `get_gpjy_value()` | 按范围取股票交易数据 |
| GPJYONE | `get_gpjy_value_by_date()` | 按日期取股票交易数据 |
| SCJYVALUE | `get_scjy_value()` | 按范围取市场交易数据 |
| SCJYONE | `get_scjy_value_by_date()` | 按日期取市场交易数据 |
| EXTERNSTR | 无直接对应 | 公式层函数，Python API 通过 `get_stock_info()` 等覆盖其功能 |
| EXTERNVALUE | 无直接对应 | 同上 |
| SIGNALS_SYS | 无直接对应 | 公式层函数，需在 TDX 中创建自定义公式引用 |
