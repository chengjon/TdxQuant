# USER_FEATURES

> 本文件面向使用者，回答“当前拿这个项目能直接做什么”。
>
> 工程级实现状态、证据和边界仍以 [`FUNCTION_TREE.md`](FUNCTION_TREE.md) 为准；本文件只做用户视角的功能导航。

## 1. 推荐入口

日常优先使用 `catalog`、`task`、`trade`、`report` 四类入口：

```powershell
python -m tdxquant.cli catalog list --kind all --view summary
python -m tdxquant.cli catalog plan --entry daily-review
python -m tdxquant.cli catalog run --entry recent-ledger --view summary
```

当前 catalog 已登记大量日常 entry 和 bundle，用于把报表、交易、任务、自选股和审计复盘收口成较短命令。`catalog plan` 只预览，不执行真实业务动作。

## 2. 行情与基础数据

用户可以直接查询通达信/TdxQuant 数据能力：

- 行情快照：`api snapshot`、`tdx-data-snapshot`
- K 线：`api kline`、`tdx-data-kline`
- 分笔/Tick：`api full-tick`
- 股票信息：`stock-info`、`more-info`、`cb-info`
- 股票列表、板块列表、板块成分：`stock-list`、`sector-list`、`sector-stocks`
- 财务数据：`financial-data`、`financial-data-by-date`
- 股票、板块、市场交易数据：`*-transaction-data`
- 交易日、缓存刷新、K 线刷新、文件下载：`trading-dates`、`refresh-cache`、`refresh-kline`、`download-file`

示例：

```powershell
python -m tdxquant.cli api snapshot --code 000001
python -m tdxquant.cli api kline --code 000001 --period 1d --count 100
```

边界：真实 live 查询依赖 Windows 原生 TDX/TdxQuant 运行环境；replay/fixture 只用于离线验证契约，不能替代真实行情源。

## 3. 公式与选股

用户可以直接调用公式和批量扫描入口：

- 单公式选股/指标：`api formula-xg`、`api formula-zb`
- 批量选股/指标：`api formula-mul-xg`、`api formula-mul-zb`
- 公式筛选：`api formula-screen`
- 场景化公式扫描：`task formula-scan`
- 板块公式扫描：`task sector-formula-scan`
- 公式能力发现：`api formula-capabilities`

示例：

```powershell
python -m tdxquant.cli task formula-scan --formula-name MY_FORMULA --code 000001 --code 000002
```

边界：`formula.screen` 的 provider contract 更稳定；部分公式能力仍是 bridge-only，真实执行依赖 Windows 原生 TDX 环境。

## 4. 自选股与板块

当前可直接使用的自选股/板块功能：

- 读取自选股板块快照：`task block-read-watchlist`
- 查看完整诊断视图：`task block-read-full`
- 导出 watchlist：`task block-read-watchlist-export`
- 同步 watchlist：`task block-sync`
- JSON/CSV/TXT 导入 dry-run：`task block-watchlist-import`
- catalog 快捷入口：`read-zxg-watchlist`、`read-zxg-full`、`read-zxg-review-and-export`

示例：

```powershell
python -m tdxquant.cli task block-read-watchlist --block-code ZXG
python -m tdxquant.cli catalog run --bundle read-zxg-review-and-export
```

边界：真实写入必须显式使用非 dry-run 参数，并受 mutation/audit/write-policy 约束。

## 5. 场景化任务

`task` 层适合用户高频调用：

- 板块研究：`task sector-research`
- 公式扫描：`task formula-scan`
- 自选股总览：`task watchlist-overview`
- 自选股导出：`task watchlist-export`
- 环境刷新：`task refresh-environment`
- 订阅 watch：`task subscription-watch`
- 交易编排：`task trade-buy`、`task trade-sell`、`task trade-submit-once`、`task guarded-trade-buy`
- 预设运行：`task presets`、`task run --preset ...`

示例：

```powershell
python -m tdxquant.cli task refresh-environment --profile maintenance
python -m tdxquant.cli task watchlist-overview --code 000001 --code 000002
```

## 6. 平安证券桌面交易

当前项目可直接使用的实盘桌面交易能力主要集中在平安证券客户端：

- 交易前检查：`trade health`、`trade preflight`、`trade dialog-readiness`
- 常规买入/卖出：`trade buy`、`trade sell`
- 完整提交链路：`trade submit-once`
- 分步提交：`trade submit-ready`、`trade confirm-current`
- broker-neutral 入口：`trade order-place`、`trade order-query`、`trade trade-query`
- 预设入口：`trade presets`、`trade run --preset ...`
- catalog 快捷入口：`balanced-buy`、`turbo-buy`、`submit-once`

示例：

```powershell
python -m tdxquant.cli trade buy --port COM3 --code 516820 --price 0.35 --quantity 100
python -m tdxquant.cli trade run --preset turbo-buy --code 516820 --price 0.35 --quantity 100
```

运行前提：

- 必须在 Windows 原生 Python 下操作桌面控件。
- 平安证券客户端需要已启动、已登录、窗口状态可用。
- 完整提交链路依赖 HID 串口设备。
- 实盘交易前必须自行确认账户、标的、价格、数量和风控参数。

## 7. 交易台账、日报与审计

用户可以直接查看交易记录、日报和审计复盘：

- 最近台账：`report ledger`
- 当日交易日报：`report daily`
- 区间复盘：`report period`
- 订单/合同号查询：`report lookup`
- audit 查询：`report audit-lookup`
- 当日 audit 复盘：`report audit-daily`
- 区间 audit 复盘：`report audit-period`
- 跨 ledger/audit 查询：`task trade-audit-cross-ledger-query`
- 常用 catalog entry：`daily-review`、`daily-success`、`recent-ledger`、`recent-failures`、`audit-daily-review`、`audit-pingan-review`

示例：

```powershell
python -m tdxquant.cli report daily --view summary
python -m tdxquant.cli catalog run --entry recent-ledger --view summary
```

边界：这些功能读取本地 runtime/audit/ledger artifact；不主动查询券商后台，也不推断账户余额、手续费、PnL 或最终成交质量。

## 8. 订阅与长跑监控

当前可用入口：

- one-shot 订阅命令：`api subscription-subscribe`、`api subscription-unsubscribe`、`api subscription-list`
- 前台 watch 任务：`task subscription-watch`
- bridge 控制面：`bridge serve`、`bridge watch-start`、`bridge watch-stop`、`bridge watch-status`
- 事件读取：`bridge watch-events`、`bridge watch-events-stream`

边界：长跑治理已有状态摘要和人工复核建议，但不是完整生产 daemon 运维系统。

## 9. 诊断、探测与离线验证

排错和环境验证时可直接使用：

- TDX 环境诊断：`tdx-health`、`tdx-doctor`、`tdx-capabilities`
- 平安/桌面控件探测：`inspect`、`detect`、`uia-inspect`、`uia-dialogs`
- UIA 控件操作：`uia-click`、`uia-set-text`、`uia-read`、`uia-activate`
- Win32 控件操作：`win32-read`、`win32-set-text`、`win32-click`
- HID 测试：`hid-ping`、`hid-send`
- provider replay：`provider-replay serve`、`provider-replay config-check`、`provider-replay status`

这些命令主要用于诊断、复现和联调，不应被误认为新的业务能力。

## 10. 当前明确不可当作直接可用功能

- 通达信完整自动下单：当前只支持探测/诊断和 HID 辅助输入，尚未解决交易业务层接受证券代码输入的问题。
- 通达信原生插件 DLL 运行：当前只有示例资产和 ABI 文档，没有编译、部署、加载、绑定、执行闭环。
- 多券商完整交易平台：当前实际可用 broker 主要是平安桌面链路。
- 生产级 daemon 运维平台：已有 bridge/replay/control plane，但不是完整进程管理和生产运维系统。
