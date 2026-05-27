# USER_FEATURES 1-7 Test Report

> 测试对象：[`USER_FEATURES.md`](USER_FEATURES.md) 中第 1-7 项用户可用功能。
>
> 测试日期：2026-05-27
>
> 安全边界：允许 live TDX 只读查询；平安证券 HID 串口固定为 COM3；不允许真实交易提交；不允许非 dry-run 写入。

## 总结

第 1-7 项用户侧功能已完成第一轮全面验证。自动化回归已覆盖 CLI/API/task/report/trade/bridge/replay 契约；live TDX 只读行情与公式能力已通过冒烟验证；平安证券交易链路只执行 health/preflight/dialog-readiness 和 HID ping，不执行任何真实下单提交。

本轮测试中发现并修复的问题已提交：

- `8bdc5bf Fix report ledger fallback for Ping An submissions`
- `b9bce8a Polish report and replay CLI behavior`
- `03f7a1d Stabilize Windows pytest regression suite`

## 自动化回归

已通过：

```powershell
python -m pytest -q
```

结果：

```text
1180 passed, 1 skipped in 217.63s
```

回归覆盖重点：

- catalog/task/report/trade CLI 参数解析与派发。
- TdxApiManager/TdxTaskManager 用户级命令契约。
- replay provider 与 fixture 契约。
- 板块、自选股、导入、同步 dry-run 与治理边界。
- 平安证券交易 manager、ledger、audit、broker-neutral facade。
- bridge HTTP、订阅 watch、后台控制面。

## 功能项验证矩阵

| USER_FEATURES 项 | 用户功能 | 验证方式 | 结论 |
| --- | --- | --- | --- |
| 1 | 推荐入口 catalog/task/trade/report | `catalog list/plan/run` 自动化与 CLI 回归 | 通过 |
| 2 | 行情与基础数据 | live TDX 只读 `api health/snapshot/kline`，replay/manager 回归 | 通过 |
| 3 | 公式与选股 | `formula-capabilities` live/replay，`formula-screen` replay 回归 | 通过 |
| 4 | 自选股与板块 | `block-read-watchlist`、`block-sync`、watchlist import dry-run 回归 | 通过 |
| 5 | 场景化任务 | `watchlist-overview` live 只读，task preset/dispatch 回归 | 通过 |
| 6 | 平安证券桌面交易 | COM3 HID ping、health/preflight/dialog-readiness dry-run/只读路径 | 条件通过 |
| 7 | 交易台账、日报与审计 | `report ledger/daily`、catalog recent-ledger、audit/report 回归 | 通过 |

## Live 只读与安全验证

已执行且通过的 live/read-only 检查：

```powershell
python -m tdxquant.cli api health --profile tdx_quant_live --window-key 通达信金融终端 --hid-port COM3
python -m tdxquant.cli api snapshot --profile tdx_quant_live --code 000001.SZ --field Now --field Volume
python -m tdxquant.cli api kline --profile tdx_quant_live --code 000001.SZ --period 1d --count 5
python -m tdxquant.cli task watchlist-overview --profile tdx_quant_live --code 000001.SZ --code 000002.SZ
python -m tdxquant.cli api formula-capabilities
python -m tdxquant.cli api formula-screen --provider-mode replay --formula-name UPN --code 000001.SZ
python -m tdxquant.cli api block-read-watchlist --provider-mode replay --block-code ZXG
```

已执行且通过的 report/catalog 检查：

```powershell
python -m tdxquant.cli report ledger --ledger-jsonl-path runtime\pingan-submission-ledger.jsonl --limit 2 --view summary
python -m tdxquant.cli report daily --view summary
python -m tdxquant.cli catalog run --entry recent-ledger --view summary
```

已执行的平安证券安全检查：

```powershell
python -m tdxquant.cli hid-ping --port COM3 --timeout 2.0
python -m tdxquant.cli trade health --port COM3 --timeout 2.0
python -m tdxquant.cli trade preflight --port COM3 --timeout 2.0 --code 516820 --price 0.35 --quantity 100 --max-price 0.36
python -m tdxquant.cli trade dialog-readiness --port COM3 --timeout 2.0
```

结果：

- HID COM3 ping：通过，返回 `OK PONG`。
- `trade health` / `trade preflight` / `trade dialog-readiness`：未提交交易；风险参数校验和 HID 检查路径可达；当前因平安证券窗口未打开而返回 `window_not_found` 或无确认弹窗，这是环境前置条件失败，不是交易提交。

## 边界与未覆盖项

- 未执行任何 `trade buy/sell/submit-once/confirm-current` 的真实提交路径。
- 未执行任何非 dry-run 的自选股/板块写入。
- 平安证券完整桌面链路仍需要客户端已启动、已登录、窗口可见，并由操作者确认真实账户、标的、价格、数量和风控参数后才能进入下一轮 UAT。
- 本报告只证明 `USER_FEATURES.md` 第 1-7 项在当前安全边界下可用；工程级功能注册与边界仍以 [`FUNCTION_TREE.md`](FUNCTION_TREE.md) 为准。
