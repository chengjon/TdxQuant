# Dict

## 常量枚举
> Source: https://help.tdx.com.cn/quant/docs/markdown/Dict.html

### 市场类型
| 名称 类型 数值 说明
| .SZ int 0 深圳交易所
| .SH int 1 上海交易所
| .BJ int 2 北京交易所
| .NQ int 44 新三板
| .SHO int 8 上海个股期权
| .SZO int 9 深圳个股期权
| .HK int 31 香港交易所
| .US int 74 美国股票
| .CSI int 62 中证指数
| .CNI int 102 国证指数
| .HG int 38 国内宏观指标
| .CFF int 47 中金期货
| .CZC int 28 郑州期货
| .DCE int 29 大连期货
| .SHF int 30 上海期货
| .GFE int 66 广州期货
| .INE int 30 上海能源
| .HI int 27 港股指数
| .OF int 33 开放式基金净值
| .CFFO int 7 中金所期权
| .CZCO int 4 郑州期货期权
| .DCEO int 5 大连期货期权
| .SHFO int 6 上海期货期权
| .GFEO int 67 广州期货期权
| .QHZ int 42 期货类指数

### dividend_type复权类型
| 名称 类型 数值 说明
| type str none 不复权
| type str front 前复权
| type str back 后复权

### period周期入参类型
| 名称 类型 数值 说明
| period str 1m 1分钟
| period str 5m 5分钟
| period str 15m 15分钟
| period str 30m 30分钟
| period str 1h 60分钟（1小时）
| period str 1d 1天
| period str 1w 1周
| period str 1mon 1月
| period str 1q 1季
| period str 1y 1年
| period str tick 分笔

### order_type类型
| 名称 类型 数值 说明
| STOCK_BUY int 0 买
| STOCK_SELL int 1 卖
| CREDIT_BUY int 0 担保品买入
| CREDIT_SELL int 1 担保品卖出
| CREDIT_FIN_BUY int 69 融资买入
| CREDIT_SLO_SELL int 70 融券卖出
| CREDIT_COV_BUY int 71 买券还券
| CREDIT_STK_REPAY int 76 卖券还款
| ETF_PURCHASE int 45 基金申购
| ETF_REDEMPTION int 46 基金赎回
| FUTURE_OPEN_LONG int 101 期货开多
| FUTURE_OPEN_SHORT int 102 期货开空
| FUTURE_CLOSE_LONG int 103 期货平多
| FUTURE_CLOSE_SHORT int 104 期货平空
| OPTION_OPEN_LONG int 201 期权开多
| OPTION_OPEN_SHORT int 202 期权开空
| OPTION_CLOSE_LONG int 203 期权平多
| OPTION_CLOSE_SHORT int 204 期权平空

### price_type类型
| 名称 类型 数值 说明
| PRICE_MY int 0 自填价
| PRICE_SJ int 1 市价
| PRICE_ZTJ int 2 涨停价/笼子上限
| PRICE_DTJ int 3 跌停价/笼子下限

### Status类型
| 名称 类型 数值 说明
| WTSTATUS_NULL int 0 无效单
| WTSTATUS_NOCJ int 1 未成交
| WTSTATUS_PARTCJ int 2 部分成交
| WTSTATUS_ALLCJ int 3 全部成交
| WTSTATUS_BCBC int 4 部分成交部分撤单
| WTSTATUS_ALLCD int 5 全部撤单

---
