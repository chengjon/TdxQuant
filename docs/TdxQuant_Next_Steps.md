# TdxQuant Next Steps

本文是 `TdxQuant` 项目的统一下一步开发与改进方向说明。

它不是 `mystocks` 或 `quantix-rust` 的项目文档，而是基于两个上层项目的反馈，整理出的 **TdxQuant 自身 canonical next steps**，用于帮助上层项目提前对齐：

- TdxQuant 接下来会补哪些能力
- 哪些接口会优先稳定
- 哪些边界会被明确强化
- 哪些高风险能力会继续后置或隔离

## 1. 这份文档的定位

这份文档面向两类读者：

- TdxQuant 自身开发者
- 依赖或准备接入 TdxQuant 的上层系统

它的作用不是复述所有讨论过程，而是把当前已经收敛出的结论固化成一份项目级路线图。

输入依据主要来自：

- [TdxQuant_Project_Function_Map.md](/opt/iflow/TdxQuant/docs/TdxQuant_Project_Function_Map.md)
- [TdxQuant_Integration_Questions.md](/opt/iflow/TdxQuant/docs/TdxQuant_Integration_Questions.md)
- [TdxQuant_Integration_Questions_Quantix.md](/opt/iflow/TdxQuant/docs/TdxQuant_Integration_Questions_Quantix.md)
- `/opt/claude/mystocks_spec/docs/reports/analysis/TDXQUANT_INTEGRATION_QUESTIONS_RESPONSE_MYSTOCKS_2026-04-28.md`
- `/opt/claude/quantix-rust/docs/reviews/2026-04-28-tdxquant-integration-questions-reply.md`

## 2. 已经明确的项目方向

经过两边反馈，TdxQuant 的下一阶段定位已经比较清楚：

- TdxQuant 不是上层系统的主数据服务替代品。
- TdxQuant 不是上层系统的主任务编排中心。
- TdxQuant 不是当前优先建设的标准化交易中心。
- TdxQuant 更适合成为 `Windows 侧 TongDaXin capability provider`。

更具体地说，TdxQuant 下一步应重点发展成：

- 通达信特有能力提供层
- 稳定 machine contract 输出层
- Windows provider / bridge 可消费能力层
- 查询主线与交易主线明确分离的本地量化能力层

## 3. 两个上层项目的共同结论

虽然 `mystocks` 和 `quantix-rust` 各自侧重点不同，但它们对 TdxQuant 的核心期待高度一致。

共同结论包括：

- 接受 `Windows sidecar / provider` 模型。
- 不希望直接深耦合到 Linux/WSL 主进程。
- 不希望把 Python import 当成唯一正式集成面。
- 更偏好稳定 `HTTP + JSON / JSONL`，`CLI + JSON` 可作为过渡或 PoC。
- 认为最有价值的差异化能力是：
  - `formula`
  - `subscription`
  - `block`
- 不希望当前把 `desktop trade` 接入主执行链路。
- 要求尽快稳定 machine-readable contract。
- 要求提供 capability discovery / health probe。
- 要求查询路径与交易路径明确隔离。
- 对已稳定的 provider contract，更偏好补薄 task/report/catalog 入口，而不是再复制一层新语义。

这意味着，TdxQuant 的下一步重点已经不是“再补更多原子函数”，而是把现有能力整理成 **稳定可集成的 provider contract**。

## 4. 核心开发方向

建议后续工作收敛为以下 7 个主方向。

### 方向 A：固定同步 JSON contract

这是第一优先级。

TdxQuant 已经有较多查询和公式能力，但还没有形成对上层项目足够稳定的统一结果协议。下一步应优先固定同步调用的 JSON 包络。

建议基础字段至少包括：

- `success`
- `code`
- `message`
- `capability`
- `capability_version`
- `schema_version`
- `request_id`
- `started_at`
- `finished_at`
- `elapsed_ms`
- `runtime`
- `warnings`
- `data`
- `artifacts`

还应同时固定：

- 时间格式
- symbol 格式
- 枚举字面值
- 错误结构
- CLI 退出码语义

如果这一步不先做，上层项目很难建立长期稳定的数据模型和 contract test。

### 方向 B：建设 capability discovery / health probe

这是与同步 JSON contract 并列的高优先级工作。

上层项目不希望在调用失败后才知道当前 capability 不可用，而希望在调用前就能探测：

- 当前平台是否支持
- TongDaXin 是否启动
- `TPythClient.dll` 是否可用
- query runtime 是否可用
- subscription runtime 是否可用
- window probe / HID 是否可用
- 当前暴露了哪些 capability
- 每个 capability 的稳定性和副作用级别

这意味着 TdxQuant 需要建设统一的：

- `capabilities`
- `health`
- `doctor`
- `preflight`

这类响应必须是标准 JSON，而不是自由文本。

### 方向 C：把公式能力整理成第一条稳定 provider contract

两个上层项目都认为 `formula` 是 TdxQuant 当前最有差异化价值的能力。

因此，最合理的第一条正式 contract 应该围绕 `formula.screen` 或同类公式筛选能力展开。

优先目标不是继续扩公式函数数量，而是先稳定：

- 输入字段
- 输出 schema
- 错误路径
- 批量结果结构
- capability naming

第一条最适合对外联调的 PoC 路径应是：

- `公式选股 -> 标准股票列表 -> 上层 watchlist`

可选扩展是：

- `公式选股 -> 标准股票列表 -> TongDaXin block`

对 `block` 这条线，当前更合适的推进方式也已经更明确：

- provider 级 `block.sync_watchlist` 继续作为 canonical contract
- `task block-sync` / `task block-read-watchlist` / `task block-read-watchlist-export` 这类入口只做标准 task metadata、profile 默认值与日常命令收口
- `task block-read-watchlist` 继续直接保留 `block.read_watchlist_snapshot` / `data.snapshot` 的 provider contract
- `task block-read-watchlist-export` 继续只把 `data.snapshot` 安全写到单文件 JSON，不反向定义新的 provider schema
- 避免在 task 层复制第二套 block sync result schema

### 方向 D：把订阅底层能力产品化成长期契约

当前订阅 session 底层已经完成，并且已经形成了前台 task + worker bridge 两层可消费 contract。

截至 `2026-05-01`，前台 `subscription-watch` 已经进一步收口为 run artifact contract：

- 每次运行创建独立 `run_id` 目录
- canonical `events.jsonl`
- `status.json` / `summary.json` / `manifest.json`
- `CSV` 仅保留兼容导出角色

截至 `2026-05-03`，这条线又补齐了一层 worker bridge control plane：

- worker-local single-active background control
- worker 侧 `tdxquant bridge serve --config runtime/bridge/worker-bridge.json`
- Master 侧静态 worker registry
- 远程 `watch-start / watch-stop / watch-status`
- `list / artifacts / events / logs / health` HTTP endpoint
- bridge auth preconditions：`Authorization: Bearer <token>` + `master_allowlist` source-IP enforcement

下一步不应只停留在：

- `open_subscription_session()`
- `subscribe_hq()`

这意味着“产品化为更稳定的任务或 worker 形态”这一层已经有了第一版落地：

- 前台：`subscription-watch`
- 后台控制：worker-local single-active watch
- 远程 transport：HTTP bridge v1
- Master 发现方式：静态 worker registry

当前剩余重点不再是从 0 到 1 地补 `start / stop / status / list`，而是继续强化：

- reconnect/backoff
- 更强的长期运行治理
- 更细的 health / watermark / heartbeat 摘要
- 更广的 integration / contract regression coverage

截至 `2026-05-03`，这条 resilience 主线已经收口出明确 contract：

- live watch 在断线恢复前后保持同一个 `run_id`
- `watch_status.state=reconnecting / degraded` 已成为正式运行态摘要，而不是临时内部细节
- `status.json` / `summary.json` 已承担 heartbeat、reconnect 计数、degraded 摘要等状态输出
- `GET /bridge/v1/watch/status` 只做 controller projection，`/bridge/v1/health` 与 active `run_id` fallback 走 control-only read path
- Master registry/client 的 auth、allowlist、invalid JSON、connection refused、HTTP non-JSON failure 已固定为 transport-scoped machine error
- CLI `bridge health/watch-status/watch-list/watch-artifacts/watch-events/watch-logs` 已固定为透传 registry/client payload 的远程读命令

这里同样需要区分：

- `control.state` 是 background/bridge control-plane 状态
- `watch_status.state` 是 `subscription-watch` runtime-state summary

因此这条线接下来的重点更偏向：

- 调整 replay / fixture / contract regression coverage 与新状态对齐
- 继续验证 background / bridge / replay 对同一套 resilience 字段的兼容性
- 只在必要时扩展读模型，不引入第二套并行 lifecycle contract

建议事件 JSONL 从第一版起就固定至少这些字段：

- `schema_version`
- `session_id`
- `provider_instance_id`
- `subscription_id`
- `sequence`
- `event_type`
- `symbol`
- `source_ts`
- `event_ts`
- `reconnect_metadata`
- `payload`

### 方向 E：让 block 能力进入“可写但受治理”的状态

`block` 是高价值能力，但写入行为会改变 TongDaXin 客户端状态，因此不能只按普通查询能力处理。

截至 `2026-04-28`，这条线已经补齐第一版治理基础：

- write audit log
- mutation result schema
- failure feedback
- 可选 `mutation_key`

截至 `2026-05-03`，这条线已经补齐第一版 provider-level `block sync`：

- `watchlist -> TongDaXin block`
- `replace` / `merge`
- `create_if_missing`
- `dry_run`
- sync-level `mutation_key` replay / conflict

当前剩余重点收缩为：

- 继续围绕 `TongDaXin block -> 上层 watchlist` 打磨集成面，而不是补新的薄 task 包装
- 文件导入式 watchlist 适配
- 更高阶的覆盖写 / 增量写任务化入口

这样 `block` 才适合作为：

- watchlist -> TongDaXin block
- TongDaXin block -> 上层 watchlist

这类同步能力的正式基础。

### 方向 F：为跨项目接入提供 replay / fake / contract test 夹具

这是 `quantix-rust` 特别强调、但实际上对所有上层项目都很重要的一项。

如果 TdxQuant 只能依赖真实客户端和真实桌面环境验证，那么后续升级会非常难控。

因此需要逐步提供：

- 固定输入样例
- 固定 JSON 输出样例
- 固定 JSONL 事件样例
- replay 模式
- fake provider 模式
- contract test 夹具

截至 `2026-05-02`，这条线已经补齐两层基础设施：

- 包内稳定 fixture 资产
- 统一 manifest / loader helper
- `formula.screen` / `runtime.capabilities` / `runtime.health` / `runtime.doctor` / `block mutation` / `subscription event` / `subscription-watch run artifact` representative samples
- in-process fake provider mode
- `subscription-watch` completed-run replay materialization
- CLI subprocess replay hardening groundwork：supported replay matrix、selector precedence、stable replay failure envelope、stdout / `--output` mirroring contract

当前剩余重点收缩为：

- transport-level replay / integration hardening
- 更大范围 capability 覆盖
- 可能的后台 `subscription-watch start/stop/status/list`

也就是说，CLI subprocess replay 这一层现在已经从“待建设”转成“已完成基础 contract 固化”；后续 replay 工作主要是更高一层 transport / integration follow-up，而不是继续扩写当前这层 CLI 失败语义。

这些夹具应优先服务：

1. TdxQuant 自测
2. provider / bridge contract test
3. 上层项目端到端联调

### 方向 G：继续隔离交易主线，并补风险治理

交易线不会消失，但它不是当前对外主接入面。

后续方向应明确：

- `query / formula / block / subscription` 作为主接入能力线
- `desktop trade` 作为高风险独立 capability

交易线至少应继续补齐：

- `experimental / beta / stable` 级别标记
- `read_only / local_state_mutating / live_side_effecting` 副作用分级
- 显式 pre-confirm / confirm-current 分步边界
- durable audit log
- broker/runtime health check

截至 `2026-04-29`，这条线已经补齐第一版安全治理切片：

- 稳定、无副作用的 `trade health` broker/runtime preflight
- 稳定、无副作用的 `trade preflight` single-request readiness summary
- 稳定、会停在确认框前的 `trade submit-ready` pre-confirm boundary summary
- 稳定、会推进当前确认框的 `trade confirm-current` current-confirm + optional result-close summary
- 稳定、无副作用的 `trade dialog-readiness` confirm/result lookup readiness summary
- `trade_safety` 标准摘要
- `beta` / `local_state_mutating` / `live_side_effecting` 分级结果
- 幂等型 `submission_key`
- 基于请求校验和 `max_price` 的前置风险门
- durable submission ledger
- 同 key 重复请求短路与冲突拒绝
- 稳定 task workflow 对 `submission_key` / `max_price` 的透传
- `task run --preset ...` 对同一组交易安全参数的保留与显式覆盖
- `TdxTaskManager.trade_submit_ready(...)`
- `TdxTaskManager.trade_confirm_current(...)`
- `task trade-submit-ready ...`
- `task trade-confirm-current ...`
- `task run --preset ...` 对 split-step workflow 的收口
- 不可变 `trade_audit` JSON artifact
- `trade_audit` 与 state / event artifact 的关联回灌
- `TdxTaskManager.trade_audit_lookup(...)`
- `TdxTaskManager.trade_audit_daily_report(...)`
- `TdxTaskManager.trade_audit_period_report(...)`
- `task trade-audit-lookup ...`
- `task trade-audit-daily-report ...`
- `task trade-audit-period-report ...`
- `report audit-lookup ...`
- `report audit-daily ...`
- `report audit-period ...`
- `trade_audit` daily / period workflow 支持单状态 `status` 和多状态 `statuses` OR 过滤
- CLI 支持 `--status-any ...` 多次传入异常状态集合
- `trade_audit` daily / period workflow 支持单方法 `method` 和多方法 `methods` OR 过滤
- CLI 支持 `--method-any ...` 多次传入方法集合
- `trade_audit` 日常入口已覆盖 `confirm_current + rejected|failed` 的多维异常视角
- `trade_audit` 日常入口已覆盖 `buy_submit_once + rejected|failed` 的多维异常视角
- `trade_audit` 日常入口已覆盖 `buy + rejected|failed` 的多维异常视角
- `trade_audit` 日常入口已覆盖 submit path `buy_submit_once + confirm_current + rejected|failed` 的多维异常视角
- `trade_audit` 日常入口已覆盖 broker-scoped submit path `pingan + buy_submit_once + confirm_current + rejected|failed` 的多维异常视角
- report presets：`audit-daily-review` / `audit-daily-confirmed` / `audit-daily-rejected` / `audit-daily-replayed` / `audit-daily-failed` / `audit-daily-exceptions` / `audit-daily-confirm-exceptions` / `audit-daily-submit-once-exceptions` / `audit-daily-buy-exceptions` / `audit-daily-submit-path-exceptions` / `audit-daily-pingan-submit-path-exceptions` / `audit-period-review` / `audit-period-confirmed` / `audit-period-rejected` / `audit-period-replayed` / `audit-period-failed` / `audit-period-exceptions` / `audit-period-confirm-exceptions` / `audit-period-submit-once-exceptions` / `audit-period-buy-exceptions` / `audit-period-submit-path-exceptions` / `audit-period-pingan-submit-path-exceptions`
- catalog entries：`audit-daily-review` / `audit-daily-confirmed` / `audit-daily-rejected` / `audit-daily-replayed` / `audit-daily-failed` / `audit-daily-exceptions` / `audit-daily-confirm-exceptions` / `audit-daily-submit-once-exceptions` / `audit-daily-buy-exceptions` / `audit-daily-submit-path-exceptions` / `audit-daily-pingan-submit-path-exceptions` / `audit-period-review` / `audit-period-confirmed` / `audit-period-rejected` / `audit-period-replayed` / `audit-period-failed` / `audit-period-exceptions` / `audit-period-confirm-exceptions` / `audit-period-submit-once-exceptions` / `audit-period-buy-exceptions` / `audit-period-submit-path-exceptions` / `audit-period-pingan-submit-path-exceptions`
- audit bundles：`audit-diagnostics` / `audit-rejection-diagnostics` / `audit-confirmed-review` / `audit-replay-review` / `audit-failure-diagnostics` / `audit-exception-diagnostics` / `audit-confirm-exception-diagnostics` / `audit-submit-once-exception-diagnostics` / `audit-buy-exception-diagnostics` / `audit-submit-path-exception-diagnostics` / `audit-pingan-submit-path-exception-diagnostics`
- task presets：`submit-ready-default` / `confirm-current-default`
- split-step catalog entries：`task-submit-ready` / `task-confirm-current`
- split-step bundles：`confirm-audit-review` / `confirm-complete-review` / `confirm-exception-review` / `submit-once-exception-review` / `guarded-buy-exception-review` / `confirm-submit-path-exception-review` / `confirm-pingan-submit-path-exception-review`
- 基于 `audit_id` / `contract_no` / `submission_key` / `code` 的稳定审计查询
- 基于本地日期的稳定单日审计聚合
- 基于闭区间的稳定审计聚合

当前剩余治理重点已经进一步收缩为：

- `trade_audit` 更高阶的 broker / method / status 多维 review / diagnostics 组合扩展
- 分步交易 workflow 的更多日常 follow-up 组合扩展

在这些后续治理能力补齐前，交易线仍不应作为上层项目主线能力推广。

## 5. 推荐的开发顺序

基于当前两个上层项目的共同反馈，建议按下面顺序推进。

截至 `2026-04-28`，下面五包基础能力已经进入主线：

- `provider-result-contract`
- `provider-capability-discovery`
- `provider-formula-screen-contract`
- `task-runtime-subscription-watch`
- `provider-subscription-event-contract`

当前主优先级已经切到：

- `Phase 5：provider integration hardening`
- `Phase 6：更广泛的 provider-ready 整理、block sync task 与 trade safety`

其中 `block` 主线在 provider 层已经补齐了两条对称能力：

- 正向：`block.sync_watchlist(...)`
- 反向：`block.read_watchlist_snapshot(...)`

当前仍明确延期的，是围绕这条反向读取能力的更厚场景包装：

- 直接写回上层系统
- `catalog` / preset / report 层收口

### Phase 1：Provider 基础 contract（已完成基础版）

目标：

- 固定同步 JSON 包络
- 固定错误模型
- 固定 schema / capability version
- 固定 CLI 退出码语义

当前状态：

- 已完成同步 JSON envelope、错误模型、schema/capability version 和 CLI 退出码语义
- `formula.screen` 已有独立 capability-specific contract 文档

### Phase 2：Capability discovery 与分级（已完成基础版）

当前状态：

- 已提供 `capabilities` / `health` / `doctor` 响应
- 已引入 capability 稳定性分级
- 已引入 capability 副作用分级

建议 capability 至少分两套维度：

- 副作用分级：
  - `read_only`
  - `local_state_mutating`
  - `live_side_effecting`
- 稳定性分级：
  - `stable`
  - `beta`
  - `experimental`

### Phase 3：公式能力 PoC-ready（已完成基础版）

当前状态：

- `formula.screen` 已成为正式 capability name
- 已提供 `TdxApiManager.formula.screen(...)`
- 已提供 `api formula-screen`
- 已提供 `tdx-formula-screen`
- 已固定命中/未命中列表与逐 symbol 归一化 row schema
- 已补 provider-facing contract 文档

对应文档见：

- [TdxQuant_Provider_Formula_Screen_Contract.md](/opt/iflow/TdxQuant/docs/TdxQuant_Provider_Formula_Screen_Contract.md)

后续围绕公式能力的剩余工作，不再是第一条 contract 从 0 到 1，而是：

- 增补更多公式类 capability-specific contract
- 提供 replay / fake / contract fixture
- 视需要补 block 同步衔接示例

### Phase 4：订阅能力 contract-ready（已完成 foreground + bridge slice）

当前状态：

- 已提供 `TdxTaskManager.subscription_watch(...)`
- 已提供 `task subscription-watch`
- 已固定第一版 `JSONL` 事件 schema
- 已固定 `status.json` 状态文件
- 已支持 `max_events` / `max_seconds` bounded run
- 已支持前台 `Ctrl+C` 优雅退出
- 已提供 worker-local single-active background control
- 已提供 `tdxquant bridge serve --config ...`
- 已提供 Master 侧静态 worker registry 与 `bridge watch-start|watch-stop|watch-status`
- 已提供 `watch/list/artifacts/events/logs/health` HTTP bridge endpoint

对应文档见：

- [TdxQuant_Task_Subscription_Watch_Contract.md](/opt/iflow/TdxQuant/docs/TdxQuant_Task_Subscription_Watch_Contract.md)

后续围绕订阅能力的剩余工作主要是：

- reconnect/backoff 与更强运行态治理
- 更强的 bridge / worker integration regression
- future transport wrapper，例如 SSE 或更高层协调协议

### Phase 5：Block 写入治理

目标：

- block 读写分层
- 写入审计
- 幂等与失败反馈
- 为未来同步流程打基础

### Phase 6：更广泛的 provider-ready 整理

截至 `2026-05-03`，这条线已经完成第一版 query contract hardening：

- `market / meta / financial / transaction` 统一 `data.query_meta`
- CLI / manager / replay fixture / discovery metadata 对齐
- representative success / empty / failure query fixtures

当前剩余重点收缩为：

- 更大范围 query replay coverage
- 批量调用场景下的更强 contract 和 scenario task 收口
- 上层项目面向 query adapter 的集成回归

### Phase 7：交易线独立加固

目标：

- 继续补风控、审计、健康检查
- 保持不进入上层系统主执行链路

## 6. 上层项目现在就可以对齐的边界

为了便于 `mystocks`、`quantix-rust` 或其他上层系统提前适应，当前建议它们先按以下边界对齐：

- 默认按 `Windows provider` 模型接入。
- 正式长期集成面优先预期为 `HTTP + JSON / JSONL`。
- `CLI + JSON` 可作为早期 PoC 或调试路径，但不应假设是最终唯一协议。
- 不要把 `task / report / catalog` 当成正式稳定 contract。
- 优先围绕 `formula`、`subscription`、`block` 做接入准备。
- 对 `desktop trade` 保持隔离预期，不纳入当前主执行路径。
- 上层如要开始联调，应优先准备：
  - watchlist 导入路径
  - JSON contract test
  - JSONL 事件消费路径
  - capability probe 消费逻辑

## 7. 当前不建议优先推进的事项

为了防止路线再次发散，以下事项不建议作为当前第一优先级：

- 把 TdxQuant 做成 Linux/WSL 主进程内嵌库
- 直接推进 FFI / PyO3 / 深耦合嵌入
- 让 `catalog` 或 `report` 反向定义正式集成协议
- 在 contract 未固定前继续扩大量新入口
- 先推进桌面交易接入上层执行主线
- 让 `send_warn` 成为早期主接入能力

## 8. 建议的后续 OpenSpec 包

为了便于真正推进，建议下一步按小包拆开，而不是混成一个大 change。

建议候选方向：

1. `block-mutation-safety`
   - 已完成：block 写入审计、`applied / noop / rejected / failed` governance schema、失败反馈、可选 `mutation_key`、本地 replay / conflict 治理
2. `provider-replay-fixtures`
   - 已完成：包内 fixture bundle、manifest / loader、JSON / JSONL contract samples
3. `trade-safety-hardening`
   - 已完成：`trade_safety` 摘要、`submission_key`/`max_price` 风险门、durable submission ledger
4. `task-trade-safety-passthrough`
   - 已完成：稳定 task workflow 与 `task run --preset ...` 透传 `submission_key` / `max_price`
5. `trade-health-check`
   - 已完成：稳定 `trade health`、broker/runtime readiness summary、可选 HID ping
6. `trade-preflight-readiness`
   - 已完成：稳定 `trade preflight`、buy-page detect、risk gate、idempotency、HID ping 的单次请求预检
7. `trade-dialog-readiness`
   - 已完成：稳定 `trade dialog-readiness`、confirm/result dialog lookup readiness、只读可见性语义
8. `trade-submit-ready-boundary`
   - 已完成：稳定 `trade submit-ready`、pre-confirm boundary、`local_state_mutating` 安全分级
9. `trade-confirm-current-workflow`
   - 已完成：稳定 `trade confirm-current`、current-confirm boundary、可选 result closeout

## 9. 结论

把 `mystocks` 和 `quantix-rust` 的反馈合并后，TdxQuant 的 next steps 已经很清楚：

- 先把自己变成稳定的 TongDaXin provider
- 先固定 machine contract，再扩大能力面
- 先产品化 `formula`、`subscription`、`block`
- 先支持 capability discovery、grading、replay、contract test
- 继续把交易能力隔离在高风险独立路径上

一句话总结：

TdxQuant 下一步最重要的事情，不是继续横向加更多函数，而是把现有差异化能力整理成 **Windows 侧、协议稳定、可发现、可测试、可分级** 的正式集成能力层。
