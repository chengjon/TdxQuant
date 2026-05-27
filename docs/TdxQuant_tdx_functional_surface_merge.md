# TdxQuant tdx 功能面合并矩阵

> 状态说明：本文记录 `D:\MyCode3\tdx` 功能、文档和真实机联调证据并入当前仓库的采纳口径。
>
> 当前功能状态仍以根目录 [`FUNCTION_TREE.md`](../FUNCTION_TREE.md) 为唯一注册表；本文只作为本轮合并的证据索引和决策说明。

## 输入材料

本轮按用户指定的三份外部材料启动分析：

- `D:\MyCode3\tdx\README.md`
- `D:\MyCode3\tdx\docs\TdxQuant_Project_Function_Map.md`
- `D:\MyCode3\tdx\docs\pingan-tdx-win32-validation-summary.md`

同时做了针对性目录差异扫描：

- `D:\MyCode3\tdx\tdxquant` vs `D:\MyCode3\TdxQuant\tdxquant`
- `D:\MyCode3\tdx\tests` vs `D:\MyCode3\TdxQuant\tests`
- `D:\MyCode3\tdx\runtime` vs `D:\MyCode3\TdxQuant\runtime`
- `D:\MyCode3\tdx\docs` vs `D:\MyCode3\TdxQuant\docs`

## 结论摘要

当前仓库不是旧 `tdx` 的空白目标，而是已经继续演进后的主线。合并方式应为“能力级归并 + 证据采纳”，不是目录覆盖。

正式采纳的核心结论：

- 平安证券桌面买入闭环可以作为已验证能力采纳，但必须表述为混合链路：UIA 填单、HID 触发首次确认、Win32 `WM_COMMAND` 推进买入确认、HID `Enter` 关闭结果提示窗。
- 通达信交易线路只采纳为探测/诊断能力。当前证据显示它可发现控件、填字段、读字段、触发提示、通过 `Stock` 注册消息切换主证券上下文，但仍未解决交易业务层认可证券代码输入的问题。
- 当前仓库中较新的 block sync、worker bridge、provider replay、function tree registry、subscription watch background、trade audit index 等能力不得被旧 `tdx` 文件覆盖。

## 合并矩阵

| 类别 | 外部 `tdx` 内容 | 当前仓库状态 | 处理决策 |
| --- | --- | --- | --- |
| 当前仓库更新 | `tdxquant/api/*`、`tdxquant/cli.py`、`tdxquant/trade/*`、`tdxquant/trader/*` | 当前仓库包含更多 API、task、catalog、provider replay、block sync、subscription background 和 trade governance 能力 | 不从 `tdx` 覆盖源码；只在发现缺口时做能力级补丁 |
| 当前仓库更新 | `tests/` | 当前仓库有更多 focused tests，例如 block sync、bridge HTTP、provider replay、subscription watch、function tree registry、trade audit index | 不按目录导入旧测试；仅保留 `tests/pingan.py` 作为历史 scratch 候选，不进入当前默认测试面 |
| 外部有用证据 | `docs/pingan-tdx-win32-validation-summary.md` | 当前 README 中仍保留较早“平安纯非物理最终提交未打通”的口径 | 采纳最终总结：平安混合链路已打通；通达信完整下单未打通 |
| 外部有用背景 | `README.md` 与 `docs/TdxQuant_Project_Function_Map.md` | 当前仓库已有 `FUNCTION_TREE.md` 和更新后的功能图 | 仅作为背景和差异输入；最终状态写入当前 `FUNCTION_TREE.md` |
| 外部证据但不导入 | `pingan-*.json`、`tdx-*.json` 大量真实机抓取 | 多数为真实机 raw dump，部分文件体积很大，可能含账户、合同号、句柄和窗口状态 | 默认不导入；必要时只导入小型、已脱敏、可审查的样本 |
| 生成/噪声 | `__pycache__`、`.pytest_cache`、根目录巨大 raw 文件 | 当前仓库不应新增这些内容 | 明确排除 |
| 当前已有稳定证据 | `runtime/trade-audits/`、`runtime/trader/*`、`runtime/command-*.json` | 当前仓库已包含 canonical trader、audit、preset、bundle 产物 | 保持当前产物，不用旧 `tdx` 运行时目录替换 |
| 文档结构差异 | `docs/tdx-docs/*`、`docs/markitdown-*`、`docs/TestPluginTCale/*` | 当前仓库已经有转换后的 docs 和 web docs；部分外部文件是历史转换源或示例工程 | 不批量导入；后续如需要 DLL/plugin 文档再单独拆 change |

## 已采纳的交易边界

### 平安证券

采纳状态：可作为当前项目的可用桌面交易自动化实现，但不是纯后台 Win32 自动化。

稳定链路：

1. UIA 写入证券代码、价格、数量。
2. HID `Tab + Enter` 触发首次确认。
3. Win32 `WM_COMMAND` 推进买入确认窗。
4. HID `Enter` 关闭结果提示窗。
5. 命令结果、`runtime/pingan-last-order.json` 和日志回填合同号。
6. 主窗口恢复到可继续下一单状态后，才适合继续执行。

外部参考证据：

- `D:\MyCode3\tdx\docs\pingan-tdx-win32-validation-summary.md`
- `D:\MyCode3\tdx\pingan-516820-submit-once.json`
- `D:\MyCode3\tdx\pingan-after-submit-uia-v2.json`
- `D:\MyCode3\tdx\pingan-result-hid-enter.json`
- `D:\MyCode3\tdx\pingan-v2-after-hid-enter.json`

### 通达信交易线路

采纳状态：探测/诊断能力保留，完整自动下单不可标记为可用。

已验证：

- 可发现通达信买入页字段和买入按钮。
- 可写入并读回代码、价格、数量字段。
- 可通过 `post_wm_command_parent` 触发业务提示。
- 可通过 `RegisterWindowMessage("Stock")` 切换主证券上下文。

未解决：

- 自动输入证券代码后，交易业务层仍可稳定提示 `请输入证券代码!`。
- `Stock` 注册消息只能切换主证券上下文，不能替代交易页证券代码输入。

外部参考证据：

- `D:\MyCode3\tdx\docs\pingan-tdx-win32-validation-summary.md`
- `D:\MyCode3\tdx\tdx-prompt-controls.json`
- `D:\MyCode3\tdx\tdx-confirm-controls.json`
- `D:\MyCode3\tdx\tdx-confirm2-controls.json`
- `D:\MyCode3\tdx\tdx-keybd-popup-controls.json`

## 代码导入判断

本轮没有发现需要从旧 `tdx` 目录直接复制到当前源码树的新增实现。当前仓库已经包含更多后续模块和测试，包括但不限于：

- `tdxquant/block_sync.py`
- `tdxquant/block_watchlist_import.py`
- `tdxquant/bridge_http.py`
- `tdxquant/bridge_registry.py`
- `tdxquant/formula_capabilities.py`
- `tdxquant/provider_transport_replay.py`
- `tdxquant/replay_provider.py`
- `tdxquant/subscription_watch_background.py`
- `tdxquant/subscription_watch_run.py`
- `tdxquant/trade_audit_index.py`

因此本轮合并重点是文档、状态注册和证据口径，不做源码覆盖。

## 后续可拆项

- 如需把 `D:\MyCode3\tdx\docs\TestPluginTCale` 或通达信 DLL 函数文档纳入当前项目，应单独拆 plugin/DLL 文档 change。
- 如需继续攻克通达信完整下单，应单独拆 TongDaXin trade execution blocker change，先解决交易业务层认可证券代码输入的问题。
- 如需导入真实机 JSON 样本，应先做脱敏和体积筛选，再进入 `runtime/verification/`。

## 本轮验证记录

通过：

- `C:\Users\John Cheng\AppData\Local\Programs\Python\Python312\python.exe scripts\validate_function_tree_registry.py --json`
  - `valid=true`
  - `row_count=64`
  - `problem_count=0`
- `C:\Users\John Cheng\AppData\Local\Programs\Python\Python312\python.exe -m pytest -q tests\test_function_tree_registry.py tests\test_trade_manager.py tests\test_pingan_trader_gateway.py`
  - `47 passed`
- `C:\Users\John Cheng\AppData\Local\Programs\Python\Python312\python.exe -m pytest -q tests\test_hid_bridge.py`
  - `3 passed`
- `openspec validate merge-tdx-functional-surface --strict`
  - valid

受当前 Windows 本地环境限制未通过：

- `tests\test_trader_cli.py`、`tests\test_tdx_trade_bridge.py` 及多个 CLI/bridge 相关测试在收集阶段导入 `tdxquant.subscription_watch_background`，该模块直接依赖 Unix-only `fcntl`，当前 Windows Python 无该模块。
- 全量 `python -m pytest -q` 同样受 `fcntl` 阻断；此外 `tdxdata_test.py` 需要 `D:\MyCode3\TPythClient.dll`，当前环境未提供该 DLL。

以上失败点不是本轮文档/状态合并改动引入；本轮没有改动 CLI、bridge、subscription background 或 `tqcenter.py` 代码。
