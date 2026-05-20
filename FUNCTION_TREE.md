# FUNCTION_TREE

> 本文件是 TdxQuant 当前唯一的功能全景图与状态注册表。
>
> 本文件同时记录“当前可用能力”和“已设计/待实现能力”。凡是尚未可用的节点，必须显式标为 `[已设计/待实现]`，并在边界中写明“不可作为当前可用能力使用”。
>
> 不再单独维护会与本文件抢真相的 `ROADMAP.md`。后续路线、缺口和设计项统一登记在本文件的状态注册表中。

## 0. 注册规则

| 字段 | 规则 |
| --- | --- |
| 状态 | 每个功能节点必须使用 `[已实现]`、`[部分实现]`、`[已设计/待实现]`、`[非目标/边界]` 之一。 |
| 证据 | 已实现节点必须指向源码、配置、测试、运行时样例或已归档契约文档；待实现节点必须指向设计/下一步文档或明确缺口来源。 |
| 边界 | 必须说明这个节点当前能用到哪里、不能承诺什么。待实现节点必须明确写出“不代表当前可用”。 |
| 更新方式 | 新功能、新任务、新报告、新 bridge、新交易能力、新契约缺口，都先更新本文件，再删除或归并会形成第二套真相的规划文档。 |

## 1. 当前基线

| 功能节点 | 状态 | 证据 | 边界 |
| --- | --- | --- | --- |
| 项目基线 | `[已实现]` | 当前工作区；`tdxquant_py=65`、`tests=24`、`provider_fixtures=40` | 本文件描述当前工作区主线，不保证外部分支或历史 PR 一致。 |
| 单一功能注册表 | `[已实现]` | 本文件；`docs/TdxQuant_Project_Function_Map.md` 已作为输入资料归并 | `docs/TdxQuant_Project_Function_Map.md` 可作历史/背景参考，但本文件才是功能状态入口。 |
| 运行环境定位 | `[已实现]` | `README.md`：当前分支以 `WSL <-> Windows TDX bridge` 为主目标 | WSL 侧消费结构化 JSON；不直接承诺在 WSL 内操作 Win32/UIA/HID。 |

## 2. 功能全景图

```text
TdxQuant
├── A. 统一入口与治理 [已实现为主]
│   ├── CLI 命令面 [已实现]
│   ├── Manager API [已实现]
│   ├── runtime profiles / presets [已实现]
│   └── command catalog / bundle / report preset [已实现]
├── B. 查询与运行时主线 [已实现为主]
│   ├── market / meta / financial / transaction [已实现]
│   ├── formula [已实现；更多 capability contract 部分覆盖]
│   ├── block [部分实现]
│   ├── runtime 基础能力 [已实现]
│   ├── subscription session / watch / worker bridge [部分实现]
│   └── provider contract / fixtures / replay [部分实现]
├── C. 任务、报告、目录主线 [已实现为主]
│   ├── TdxTaskManager [已实现]
│   ├── task profiles / presets [已实现]
│   ├── report presets [已实现]
│   └── command catalog / command bundles [已实现]
├── D. 桌面自动化交易主线 [部分实现]
│   ├── desktop UIA / Win32 / HID primitives [已实现]
│   ├── TdxTradeManager / TradeService / PingAn gateway [已实现]
│   ├── PingAn buy / sell / submit_once / confirm [部分实现]
│   └── trade audit / ledger / safety governance [部分实现]
└── E. 待闭合与下一阶段能力 [分状态登记]
    ├── subscription query-style one-shot CLI
    ├── subscription HTTP/SSE 推送语义
    ├── provider HTTP replay service / daemon fake provider
    ├── block 文件导入式 watchlist 与写策略硬化/高阶入口
    ├── 更完整的 formula capability-specific contract
    ├── 更厚的日常 task/report/catalog 组合入口
    ├── 更高阶 trade_audit 聚合与跨 ledger 查询
    └── 桌面交易扩展 broker capability 边界
```

## 3. 状态注册表

### A. 统一入口与治理

| ID | 功能节点 | 状态 | 证据 | 边界 |
| --- | --- | --- | --- | --- |
| A-01 | CLI 命令面 | `[已实现]` | `tdxquant/cli.py` 注册约 `204` 个 parser；`tests/test_api_cli.py`、`tests/test_trader_cli.py` | 命令存在不等于每个命令都可在非 Windows 环境完成真实外部调用；外设/TDX 客户端相关命令依赖本机环境。 |
| A-02 | API Manager 统一入口 | `[已实现]` | `tdxquant/api/manager.py`：`TdxApiManager` 与 market/meta/formula/financial/transaction/runtime/block proxy | 统一入口主要封装本地/bridge 调用；不声明覆盖 TDX 原始接口全集。 |
| A-03 | Task Manager 统一入口 | `[已实现]` | `tdxquant/api/task.py`：`TdxTaskManager`；`runtime/task-profiles.json` 约 `22` 个 profile；`runtime/task-presets.json` 约 `11` 个 preset | 已有日常任务入口，但更厚的组合任务仍按具体节点登记为待实现。 |
| A-04 | Trade Manager 统一入口 | `[已实现]` | `tdxquant/trade/manager.py`：`TdxTradeManager`；`tdxquant/trader/service.py`：`TradeService`；`tests/test_trade_manager.py` | 当前重点是平安证券桌面链路；不等于多券商全量交易平台。 |
| A-05 | runtime profiles / presets | `[已实现]` | `runtime/api-profiles.json`、`runtime/task-profiles.json`、`runtime/trade-profiles.json`、`runtime/report-presets.json`、`runtime/command-catalog.json` | JSON 配置是本地入口编排层；外部服务或真实交易环境仍需对应 runtime 前置条件。 |
| A-06 | command catalog | `[已实现]` | `tdxquant/catalog.py`；`runtime/command-catalog.json` 约 `115` 个 entry；`runtime/TdxQuant_Command_Catalog_Usage.md` | catalog 描述可运行命令和参数编排，不替代能力状态判断；状态以本文件为准。 |
| A-07 | command bundle | `[已实现]` | `runtime/command-bundles.json` 约 `144` 个 bundle；`tdxquant/catalog.py` 支持 bundle 解析 | bundle 是组合执行入口；单个 step 仍受底层功能节点边界约束。 |
| A-08 | OpenSpec 生命周期材料 | `[部分实现]` | `openspec/changes/archive/**`、`openspec/specs/**`；`docs/superpowers/plans/**` | 可作为设计和归档证据，不直接证明当前代码可运行；实现状态仍以源码/测试/运行时配置为准。 |

### B. 查询与运行时主线

| ID | 功能节点 | 状态 | 证据 | 边界 |
| --- | --- | --- | --- | --- |
| B-01 | market 查询 | `[已实现]` | `tdxquant/api/market.py`；`tdxquant/api/bridge.py`：`run_tdx_market_snapshot`、`run_tdx_data_kline`、`run_tdx_full_tick`；provider fixture `market-*.json` | 依赖 TDX/bridge provider；fixture 只能证明契约和 replay，不代表实时行情环境永远可用。 |
| B-02 | meta 查询 | `[已实现]` | `tdxquant/api/meta.py`；provider fixture `meta-stock-list-success.json`、`meta-sector-stocks-success.json` | 覆盖股票列表、板块股票等常用元数据；不声明覆盖所有 TDX 字典类接口。 |
| B-03 | financial 查询 | `[已实现]` | `tdxquant/api/financial.py`；`tdxquant/api/bridge.py`：`run_tdx_financial_data`；provider fixture `financial-financial-data-*.json` | 已有财务数据桥接和 fixture；更高阶基本面分析不是当前节点承诺。 |
| B-04 | transaction 查询 | `[已实现]` | `tdxquant/api/transaction.py`；CLI parser 包含 `stock-transaction-data`、`sector-transaction-data`、`market-transaction-data` | 当前是查询入口层；性能、长时间批量拉取和缓存策略按 runtime 节点边界处理。 |
| B-05 | formula 基础接口 | `[已实现]` | `tdxquant/api/formula.py`；CLI parser 包含 `formula-format-data`、`formula-set-data`、`formula-zb`、`formula-xg` 等 | 已有常用公式入口；“公式类 capability 全覆盖”另列为部分覆盖/待实现，不在此处偷换为已完成。 |
| B-06 | formula.screen provider contract | `[已实现]` | `tdxquant/formula_screen.py`；provider fixture `formula-screen-success.json`、`formula-screen-failure.json`；相关契约文档 `docs/TdxQuant_Provider_Formula_Screen_Contract.md` | 已形成 provider contract；真实公式执行仍依赖 Windows 原生 TDX 环境。 |
| B-07 | 更多 formula capability-specific contract | `[部分实现]` | `docs/TdxQuant_Project_Function_Map.md` 标记“更多公式类 capability-specific contract [部分覆盖]” | 不可宣称所有公式能力都有稳定 provider contract；新增能力必须逐项补契约、fixture、测试。 |
| B-08 | block 用户板块读取/生命周期变更 | `[已实现]` | `tdxquant/api/block.py`、`tdxquant/block_mutation.py`；provider fixture `block-send-user-block-*.json`；`tests/test_block_sync.py` | 已支持用户板块读写相关基础能力；真实写入必须经过 mutation governance 和 dry-run/plan 约束。 |
| B-09 | block.read_watchlist_snapshot | `[已实现]` | `tdxquant/block_snapshot.py`；provider fixture `block-read-watchlist-*.json`；`tests/test_block_snapshot.py` | 当前是 watchlist 快照读取契约；不等价于任意格式导入或复杂合并写入。 |
| B-10 | block.sync_watchlist | `[已实现]` | `tdxquant/block_sync.py`；provider fixture `block-sync-*.json`；`tests/test_block_sync.py` | 已支持受控同步；覆盖写/增量写高阶入口按 E-04 登记，并继续受 provider mutation 安全边界约束。 |
| B-11 | block mutation audit / mutation_key governance | `[已实现]` | `tdxquant/block_mutation.py`；`docs/TdxQuant_Provider_Block_Mutation_Safety.md` | governance 是安全边界，不是绕过真实 TDX 客户端限制的保证。 |
| B-12 | runtime 基础能力 | `[已实现]` | `tdxquant/api/runtime.py`；CLI parser 包含 `refresh-cache`、`trading-dates`、`refresh-kline`、`download-file`、`send-warn` | 基础 runtime 命令已存在；`send-warn` 等能力不是当前主接入路径，使用前需核对本机配置。 |
| B-13 | persistent subscription session | `[已实现]` | `tdxquant/api/bridge.py`：`TdxRuntimeSubscriptionSession`、`run_tdx_open_subscription_session`；`tests/test_subscription_event_contract.py` | 提供 subscribe/unsubscribe/list 等 session 能力；长期运行治理仍按 B-16/E-01 分状态。 |
| B-14 | task subscription-watch 前台运行 | `[已实现]` | `tdxquant/subscription_watch_run.py`；`tests/test_subscription_watch_run.py`；`docs/TdxQuant_Task_Subscription_Watch_Contract.md` | 已有 bounded run、artifact contract；长跑稳定性和 reconnect/backoff 治理仍属部分覆盖。 |
| B-15 | worker bridge background control plane | `[已实现]` | `tdxquant/subscription_watch_background.py`、`tdxquant/subscription_watch_background_runner.py`、`tdxquant/bridge_http.py`、`tdxquant/bridge_registry.py`；`runtime/bridge/*.example.json`；`tests/test_bridge_http.py`、`tests/test_bridge_registry.py` | 已有 worker-local single-active 与 HTTP control plane；生产部署仍需 token、allowlist、进程管理和 Windows 环境配置。 |
| B-16 | reconnect/backoff 与长期运行治理 | `[部分实现]` | `docs/TdxQuant_Next_Steps.md` 记录 `reconnecting/degraded` 状态、heartbeat、summary 输出；fixture `subscription-watch-status-*.json` | 已有状态摘要和部分契约；更强 backoff、watermark、heartbeat 和长期治理仍未完全收口。 |
| B-17 | provider result contract | `[已实现]` | `tdxquant/result_contract.py`、`tdxquant/query_contract.py`；provider fixture `provider-result-*.json`；`tests/test_provider_result_contract.py` | 约束 provider 返回结构；不保证外部 provider 永不返回业务异常。 |
| B-18 | provider capability discovery / health / doctor | `[已实现]` | `tdxquant/provider_discovery.py`；`tdxquant/api/bridge.py`：`run_tdx_provider_capabilities`、`run_tdx_provider_health`、`run_tdx_provider_doctor`；fixture `runtime-capabilities-success.json`、`runtime-health-degraded.json`、`runtime-doctor-degraded.json` | 发现和诊断是可观测能力；不自动修复本机 TDX、COM、窗口或行情源问题。 |
| B-19 | provider fixtures / in-process replay | `[已实现]` | `tdxquant/fixtures/provider/*` 共 `40` 个 fixture；`tdxquant/replay_fixtures.py`、`tdxquant/replay_provider.py`；`tests/test_replay_fixtures.py`、`tests/test_replay_provider.py` | fixture/replay 用于契约测试和离线验证；不能替代真实行情、公式或交易联调。 |

### C. 任务、报告、目录主线

| ID | 功能节点 | 状态 | 证据 | 边界 |
| --- | --- | --- | --- | --- |
| C-01 | TdxTaskManager | `[已实现]` | `tdxquant/api/task.py`：`TdxTaskManager`；`runtime/TdxQuant_Task_Layer_Usage.md` | 提供任务编排层；单个任务的真实能力仍受对应 B/D 节点边界约束。 |
| C-02 | task profiles / presets | `[已实现]` | `runtime/task-profiles.json` 约 `21` 个 profile；`runtime/task-presets.json` 约 `9` 个 preset | profiles/presets 是默认参数和组合入口，不保证所有环境一键完成。 |
| C-03 | watchlist task/report 入口 | `[已实现]` | CLI parser 包含 `watchlist-overview`、`watchlist-export`、`block-read-watchlist`、`block-read-full`、`block-read-watchlist-export`；`docs/TdxQuant_Project_Function_Map.md` 记录 `block-read-full` 完成态 | 以当前 block 读取/同步能力为基础；文件导入式 watchlist 仍按 E-03 待实现处理。 |
| C-04 | subscription-watch task 入口 | `[已实现]` | CLI parser 包含 `subscription-watch`；`tdxquant/subscription_watch_run.py`；`tests/test_subscription_watch_run.py` | 前台 run 和 artifact 契约已可用；更高层 long-running product wrapper 仍按 E-06 登记。 |
| C-05 | report presets | `[已实现]` | `runtime/report-presets.json` 约 `101` 个 preset；`tdxquant/reporting.py` | 报表是本地 artifact 汇总/查询入口；数据完整性取决于对应 runtime/trade/task artifact 是否已生成。 |
| C-06 | trade report / audit report 入口 | `[已实现]` | CLI parser 包含 `daily-trade-report`、`trade-report-lookup`、`trade-audit-lookup`、`trade-audit-daily-report`、`trade-audit-period-report`、`trade-period-report` | 已有日常诊断和回看入口；更高阶跨 ledger 组合查询仍按 E-07 待实现。 |
| C-07 | command catalog list/plan/run | `[已实现]` | CLI parser 包含 `catalog`、`list`、`plan`、`run`；`tdxquant/catalog.py` | catalog/bundle 的 plan/run 不绕过底层能力边界；失败原因需回到具体节点诊断。 |
| C-08 | read-zxg-review-and-export bundle | `[已实现]` | `runtime/command-bundles.json` 包含 `read-zxg-review-and-export`；`docs/TdxQuant_Project_Function_Map.md` 记录该 bundle 完成态 | 以现有 watchlist/block 能力为基础；不是任意外部文件导入能力。 |

### D. 桌面自动化交易主线

| ID | 功能节点 | 状态 | 证据 | 边界 |
| --- | --- | --- | --- | --- |
| D-01 | desktop UIA primitives | `[已实现]` | `tdxquant/desktop/uia.py`、`tdxquant/uia_inspector.py`；CLI parser 包含 `uia-*` 命令 | 依赖 Windows 桌面、目标窗口和控件树稳定性；WSL 侧只能通过 bridge/JSON 消费结果。 |
| D-02 | desktop Win32 primitives | `[已实现]` | `tdxquant/desktop/win32.py`、`tdxquant/win32_api.py`；CLI parser 包含 `win32-*` 命令 | 仅适用于 Windows 客户端自动化；窗口标题、权限、焦点和消息投递策略会影响结果。 |
| D-03 | HID bridge primitives | `[已实现]` | `tdxquant/desktop/hid.py`、`tdxquant/hid_bridge.py`；CLI parser 包含 `hid-ping`、`hid-send`、`tdx-trade-hid-*`；`tests/test_hid_bridge.py` | 依赖 HID/串口设备和本机端口；测试可覆盖契约，不代表硬件永远在线。 |
| D-04 | broker / gateway abstraction | `[已实现]` | `tdxquant/trader/gateway.py`、`tdxquant/trader/registry.py`、`tdxquant/trader/models.py`、`tdxquant/brokers/base.py` | 抽象已存在；实际可用 broker 以已接入 adapter 为准。 |
| D-05 | PingAn desktop gateway | `[已实现]` | `tdxquant/trader/adapters/pingan_desktop.py`：`PingAnDesktopTraderGateway`；`tests/test_pingan_trader_gateway.py`、`tests/test_trader_gateway.py` | 当前主要服务平安证券桌面客户端；其他券商不能按此节点默认视为可用。 |
| D-06 | PingAn health / preflight / readiness | `[已实现]` | `TdxTradeManager.pingan.health/preflight/submit_ready/dialog_readiness`；CLI parser 包含 `trade health`、`trade preflight`、`submit-ready`、`dialog-readiness` | 是交易前诊断与准备检查；通过检查不等于实际下单一定成功。 |
| D-07 | PingAn buy / sell / confirm_current | `[部分实现]` | `TdxTradeManager.pingan.buy/sell/confirm_current`；`tdxquant/trade/manager.py`；`runtime/trade-audits/*`；`tests/test_trade_manager.py` | 已有买入、卖出、确认链路和审计；真实交易仍必须受 max_price、submission_key、人工/环境安全约束。 |
| D-08 | PingAn submit_once | `[部分实现]` | `TdxTradeManager.pingan.buy_submit_once`；`docs/TdxQuant_Project_Function_Map.md` 记录 `side=sell + execution_mode=submit_once` 兼容路由；CLI parser 包含 `trade-submit-once`、`submit-once` | 支持当前适配过的 submit-once 路径；不代表所有交易品种、券商、异常弹窗都已覆盖。 |
| D-09 | trade safety / idempotency governance | `[已实现]` | `tdxquant/trader/store.py`；runtime artifact `runtime/pingan-submission-ledger.jsonl`、`runtime/pingan-order-events.jsonl`；`docs/TdxQuant_Project_Function_Map.md` 记录 `submission_key` ledger、`max_price` 风险门、`trade_safety` 摘要 | governance 用于降低重复提交和危险价格风险；不替代真实交易前的人为风控。 |
| D-10 | immutable trade audit artifacts | `[已实现]` | `runtime/trade-audits/` 当前存在约 `300` 个审计 JSON；`runtime/report-presets.json` 包含大量 audit preset | artifact 可用于回看和诊断；目录数量是当前工作区样例，不保证生产保留策略。 |
| D-11 | trade_audit daily/period diagnostics | `[部分实现]` | CLI parser 包含 `trade-audit-daily-report`、`trade-audit-period-report`；`runtime/report-presets.json` 包含 pingan/rejected/failed/exceptions 等 preset | 大量常用视角已落地；更丰富 broker/method/status 组合和跨 ledger 查询仍按 E-07 登记。 |

### E. 已设计/待实现能力

| ID | 功能节点 | 状态 | 证据 | 边界 |
| --- | --- | --- | --- | --- |
| E-01 | subscription query-style one-shot CLI | `[部分实现]` | `tdxquant/api/bridge.py` 提供 `run_tdx_subscription_subscribe/unsubscribe/list` one-shot wrappers；`RuntimeApi.subscription_subscribe/unsubscribe/list` 接出 runtime API；`tdxquant/cli.py` 提供 `api subscription-subscribe`、`api subscription-unsubscribe`、`api subscription-list`；`tests/test_tdx_api_bridge.py` 与 `tests/test_api_cli.py` 覆盖 runtime wrapper、CLI parse/dispatch 与 replay rejection | 当前是 query-style one-shot 方法调用：会打开 runtime subscription session、调用一次 `subscribe_hq`/`unsubscribe_hq`/`get_subscribe_hq_stock_list` 并关闭；不启动 foreground `subscription-watch`、background worker、SSE/event-stream transport，也不补 replay fixture 或 reconnect/backoff 长跑治理。 |
| E-02 | subscription HTTP/SSE 推送语义 | `[部分实现]` | `tdxquant/bridge_http.py` 已新增 `GET /bridge/v1/watch/events/stream` SSE 投影；`tdxquant/bridge_registry.py` 已新增 master-side stream helper；`tdxquant/fixtures/provider/subscription-watch-event-stream-frames.jsonl` 与 `tests/test_bridge_http.py` / `tests/test_bridge_registry.py` / `tests/test_replay_fixtures.py` 已覆盖代表性帧 | 当前是 read-only bridge event-stream v1，投影现有 run artifacts 与 controller state；不重写 `subscription-watch` artifact contract，不改变 worker registry/auth 语义，也不代表多 worker 调度或更高层协调协议已完成。 |
| E-03 | block 文件导入式 watchlist 适配 | `[部分实现]` | `tdxquant/block_watchlist_import.py` 支持 JSON import schema、parser/validator、dry-run plan、`sync_watchlist_import_file(...)` 接线；`TdxTaskManager.block_watchlist_import`、`task block-watchlist-import`、`runtime/task-presets.json` 的 `plan-zxg-watchlist-import` 与 catalog entry；`tests/test_block_watchlist_import.py` / `tests/test_api_cli.py` 覆盖 task dispatch 与 catalog plan；OpenSpec `block-watchlist-import-task-entry` | 当前是 JSON-only adapter + task/catalog 入口；不含 CSV/TXT、双向同步或源文件回写，也不绕过现有 `block.sync_watchlist` 安全边界；catalog preset 默认 dry-run 示例，真实写入仍需显式 `--no-dry-run` 和 provider 前置条件。 |
| E-04 | block 覆盖写/增量写高阶任务入口 | `[已实现]` | `tdxquant/block_sync.py` 支持显式 `write_policy`、`mode`/`dry_run` 兼容解析、mutation_key replay/conflict 元数据和 audit policy 字段；`TdxTaskManager.block_sync`、`api/task block-sync --write-policy`、`runtime/task-presets.json` 的 `plan-zxg-block-sync-merge` 与 catalog entry；`tests/test_block_sync.py`、`tests/test_api_cli.py`、`tests/test_tdx_api_bridge.py`；OpenSpec `block-sync-write-policy-hardening` / `block-sync-write-policy-task-entry` | 当前覆盖 API/CLI/task/catalog 的显式写策略入口，catalog preset 默认 `merge_dry_run` 计划；真实写入仍需显式非 dry-run 策略/参数和 provider 前置条件，不新增 provider schema，也不绕过既有 mutation/sync 安全边界。 |
| E-05 | provider HTTP replay service | `[已实现]` | `tdxquant/provider_transport_replay.py` 提供 `GET /provider/v1/replay/health`、`fixtures`、`result`、`watch/status`、`watch/events`、`watch/events/stream`；`provider-replay serve/config-check` CLI；`runtime/provider-transport-replay.example.json`；`tests/test_provider_transport_replay.py`、`tests/test_api_cli.py`；OpenSpec `provider-transport-replay-cli-entry` | 当前是 fixture-backed、read-only、标准库 HTTP replay service；`provider-replay serve` 是前台阻塞入口，不代表后台 daemon 生命周期，不新增业务 capability，不改变 CLI subprocess replay 语义，也不等同于 live Windows provider/bridge。 |
| E-06 | daemon fake provider | `[部分实现]` | `ProviderTransportReplayHTTPServer` 支持 bearer token、allowlist、watch status/events/SSE fake provider 投影；`subscription-watch-event-stream-delayed-playback.jsonl` | 当前 fake provider 只覆盖离线只读 replay transport；没有 start/stop 生命周期控制、真实调度、真实行情会话或长期守护进程管理。 |
| E-07 | wider capability replay coverage | `[部分实现]` | 已有 `46` 个 provider fixture；`market-stock-info-success` / `market-more-info-success` / `market-cb-info-success` / `meta-gb-info-success` / `meta-ipo-info-success` / `meta-gp-one-success` 覆盖 `market.stock_info`、`market.more_info`、`market.cb_info`、`meta.gb_info`、`meta.ipo_info`、`meta.gp_one_data`；对应 `execute_sync_replay(...)`、`TdxApiManager.market/meta.*(provider_mode="replay")`、`api stock-info/more-info/cb-info/gb-info/ipo-info/gp-one --provider-mode replay` 与 `tdx-data-stock-info/more-info/cb-info/gb-info/ipo-info/gp-one --provider-mode replay` 已有 `tests/test_replay_fixtures.py` / `tests/test_replay_provider.py` / `tests/test_api_cli.py` 覆盖；OpenSpec `provider-replay-stock-info-coverage` / `provider-replay-more-info-coverage` / `provider-replay-cb-info-coverage` / `provider-replay-gb-info-coverage` / `provider-replay-ipo-info-coverage` / `provider-replay-gp-one-coverage` | 当前新增的是 stock-info、more-info、cb-info、gb-info、ipo-info、gp-one 六个 fixture-backed query 能力；`meta.divid_factors`、`transaction.*_by_date` 等未逐项补样例、契约和测试的边缘 capability 仍不承诺 replay 可用。 |
| E-08 | 更完整 formula capability-specific contract | `[部分实现]` | `docs/TdxQuant_Project_Function_Map.md` 标记 `更多公式类 capability-specific contract [部分覆盖]` | 不能把 `formula.screen` 的稳定性推广到所有公式能力。 |
| E-09 | 更厚 subscription 长跑包装 | `[部分实现]` | `SubscriptionWatchBackgroundController.status()` 返回 additive `status_summary`，汇总 control/watch_status 的 state、heartbeat、watermark、reconnect/degraded 字段；`tests/test_subscription_watch_background.py` 覆盖 stopped、running、reconnecting/degraded summary；OpenSpec `subscription-long-run-status-summary` | 当前是 long-run status summary 投影，只读保留 raw `control`/`watch_status`；不评估 wall-clock heartbeat stale，不改 reconnect/backoff 调度，不改变 start/stop/list/events/logs 或 SSE/event-stream contract。 |
| E-10 | 更多 catalog 预览/发现能力 | `[部分实现]` | `tdxquant/cli.py` 支持 `catalog preview` 非执行预览、list discovery metadata、summary-view 输出约束；`tests/test_api_cli.py` 覆盖 label/bundle discovery、entry preview、bundle preview 和 reduced summary payload；OpenSpec `catalog-discovery-preview-hardening` | 当前是 catalog CLI discovery/preview 输出硬化；不改变 `runtime/command-catalog.json` / `runtime/command-bundles.json` schema，不新增业务 contract，也不改变 `catalog run` 执行语义。 |
| E-11 | 更多 task/report 组合入口 | `[部分实现]` | `runtime/command-bundles.json` 约 `144` 个 bundle，其中约 `93` 个组合 `task` 与 `report` step；代表入口包括 `confirm-complete-review`、`submit-ready-complete-review`、`guarded-buy-complete-review`；`tests/test_api_cli.py` 覆盖 follow-up label discovery 与 `catalog plan --bundle confirm-complete-review` 非执行解析；OpenSpec `task-report-combo-entry-registry` | 当前是固定 runtime JSON preset/bundle 组合入口，不是任意 workflow builder；bundle 仍通过既有 `task` / `report` catalog entry 分发，不新增底层交易、报表或聚合语义，未覆盖的组合继续按具体节点登记。 |
| E-12 | trade_audit 高阶聚合 | `[部分实现]` | `tdxquant/trade_audit_index.py` 提供 audit index cache 与跨 `trade_audit` / submission ledger / task ledger 只读查询；`TdxTaskManager.trade_audit_cross_ledger_query` 与 `task trade-audit-cross-ledger-query` 提供入口；`tests/test_trade_audit_index.py` 和 `tests/test_api_cli.py` 覆盖缓存、join、损坏文件容错和 CLI parse | 当前是只读 exact-key 诊断查询，cache 是可重建派生 artifact；不改写历史 audit/ledger，不做成交金额/数量/价格/PnL 聚合，也不代表 live broker/provider 新能力。 |
| E-13 | 桌面交易扩展 broker capability 边界 | `[部分实现]` | `tdxquant/trade/extended_capabilities.py` 提供 PingAn desktop funds/positions/cancel/native-push capability probe；`trade broker-capabilities` 提供非执行 CLI 入口；`docs/trading/desktop_trade_extended_broker_capabilities_risk.md` 记录独立风险边界；`tests/test_trade_extended_capabilities.py` 与 `tests/test_api_cli.py` 覆盖 payload、manager 与 CLI | 当前是只读/非执行诊断边界：资金和持仓仅报告 capability metadata，撤单仅做 broker-state-mutating 分级，broker-native push 仅报告 feasibility boundary；不执行资金/持仓查询、不提交撤单、不打开 broker-native push，也不并入 query API 或默认交易主线。 |

## 4. 非目标与边界

| ID | 功能节点 | 状态 | 证据 | 边界 |
| --- | --- | --- | --- | --- |
| X-01 | WSL 内直接操作 Win32/UIA/HID | `[非目标/边界]` | `README.md` 明确 WSL 侧消费结构化 JSON，交易/数据能力优先走 Windows 原生接口或 bridge | 不在 WSL 内直接驱动桌面控件；相关操作必须在 Windows/bridge 一侧完成。 |
| X-02 | 将 fixture/replay 等同于真实外部可用性 | `[非目标/边界]` | `tdxquant/fixtures/provider/*`、`tdxquant/replay_provider.py`、`tdxquant/provider_transport_replay.py`、`tests/test_replay_provider.py`、`tests/test_provider_transport_replay.py` | fixture/replay/HTTP fake provider 是契约和回归资产；不能作为真实行情、公式、交易、Windows 客户端环境或 live bridge 已就绪的证明。 |
| X-03 | 用独立 ROADMAP 覆盖本文件 | `[非目标/边界]` | 本文件注册规则 | 不再建立与 `FUNCTION_TREE.md` 并列抢真相的 `ROADMAP.md`；待实现项只在本文件分状态登记。 |
| X-04 | 将交易主线包装成全券商生产交易平台 | `[非目标/边界]` | 当前源码主要证据集中在 `PingAnDesktopTraderGateway`、`TdxTradeManager.pingan.*`、平安相关测试与 artifact | 当前是桌面自动化交易辅助和治理层，不承诺多券商、全品种、全异常弹窗覆盖。 |

## 5. 状态变更准入

| 目标状态 | 必要证据 | 不足时的登记方式 |
| --- | --- | --- |
| `[已实现]` | 源码入口 + CLI/manager/task/report/catalog 之一 + 测试或 fixture/contract/runtime preset 证据 + 明确边界 | 缺测试或契约时只能登记为 `[部分实现]`。 |
| `[部分实现]` | 底层能力或局部入口存在，但 contract、transport、fixture、测试、日常入口或运行治理未完全闭合 | 必须在边界中写出未闭合项，并在 E 节保留待实现节点。 |
| `[已设计/待实现]` | 有设计、下一步、OpenSpec、历史计划或明确缺口来源，但没有当前稳定入口 | 必须写明“不代表当前可用”，不得放入“已实现”树枝。 |
| `[非目标/边界]` | 项目定位或安全边界明确排除 | 不得以 backlog 口吻伪装成马上要做的功能。 |

## 6. 关联文档权限

| 文档 | 当前角色 | 权限边界 |
| --- | --- | --- |
| `FUNCTION_TREE.md` | 唯一功能全景图与状态注册表 | 决定功能节点当前状态、证据和边界。 |
| `README.md` | 当前分支定位与常用入口说明 | 可说明入口和使用方式，不替代功能状态注册。 |
| `TdxQuant_handbook.md` | TdxQuant 背景/手册材料 | 可作背景阅读，不代表当前仓库实现状态。 |
| `docs/TdxQuant_Project_Function_Map.md` | 历史/背景功能地图 | 可解释背景，不覆盖本文件状态。 |
| `docs/TdxQuant_Next_Steps.md` | next-step 设计输入 | 可记录后续方向，不作为独立 roadmap 或状态表。 |
| `docs/TdxQuant_MyStocks_Next_Steps.md` | MyStocks 反馈下的设计输入 | 可记录上层反馈，不代表全项目功能状态。 |
| `docs/TdxQuant_API_System_Plan.md` | API/manager 分层设计方案 | 可解释架构分层，不决定功能是否可用。 |
| `docs/TdxQuant_Interface_Coverage_Matrix.md` | 接口覆盖对照矩阵 | 可说明接口覆盖口径，不替代功能状态注册。 |

## 7. 更新日志

| 日期 | 变更 |
| --- | --- |
| 2026-05-14 | 新增/重建根目录 `FUNCTION_TREE.md` 为“功能全景图 + 状态注册表”单一事实源；归并 `docs/TdxQuant_Project_Function_Map.md`、`README.md`、runtime 配置、源码与测试证据；明确不再单独创建 `ROADMAP.md`；补充关联文档权限表，并让 README、手册、next-step、功能地图、API 方案、接口覆盖矩阵等文档显式服从本文件；同步 `subscription HTTP/SSE 推送语义` 为 `[部分实现]`，登记 read-only bridge event-stream v1 的证据与边界。 |
