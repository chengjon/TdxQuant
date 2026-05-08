# TdxQuant Task Subscription Watch Contract

本文定义前台长驻 `subscription-watch` task 的当前 contract。

它关注的是 task lifecycle、artifact 和运行状态。

截至 `2026-05-03`，live runtime resilience contract 也已经进入这一层：

- 同一次 live run 在断线恢复前后保持同一个 `run_id`
- 同一次 live run 持续写同一个 `events.jsonl`
- reconnect / degraded 通过 `status.json` / `summary.json` 暴露，而不是拆成新 run

若只关心“单条事件行长什么样”，见：

- [TdxQuant_Provider_Subscription_Event_Contract.md](/opt/iflow/TdxQuant/docs/TdxQuant_Provider_Subscription_Event_Contract.md)

## 1. 当前入口

Python:

- `TdxTaskManager.subscription_watch(...)`

CLI:

- `tdxquant task subscription-watch ...`

这是一个 task contract，不是 provider result envelope 的同步 query contract。

## 2. 目标

`subscription-watch` 的目标是把底层 runtime subscription session 收口成一个稳定前台 workflow，供两类场景直接使用：

- 人工前台运行，持续接收订阅事件并落文件
- 上层项目先通过文件协议消费 `JSONL / CSV / status.json`

截至 `2026-05-02`，它还支持第三类场景：

- replay mode 下离线物化一份 completed run artifact bundle，而不打开 live runtime session

## 3. 输入参数

当前稳定输入至少包括：

- `stock_list`
- `max_events`
- `max_seconds`
- `poll_interval`
- `jsonl_output_path`
- `csv_output_path`
- `status_output_path`
- `provider_mode`
- `fixture`
- `fixture_path`

语义说明：

- `stock_list`：必填订阅股票列表
- `max_events`：达到事件数后自动结束
- `max_seconds`：达到运行时长后自动结束
- `poll_interval`：前台保活轮询间隔
- `provider_mode=live`：默认模式，打开真实 TongDaXin runtime subscription session
- `provider_mode=replay`：离线模式，直接从 replay source 物化 completed run
- `fixture`：显式选择 built-in replay source
- `fixture_path`：显式选择 replay manifest 或 replay run 目录
- 若不提供任何自动结束条件，则任务会一直运行到 `Ctrl+C`

`fixture` 与 `fixture_path` 互斥。

## 4. 事件 JSONL Contract

`JSONL` 文件一行一个 normalized event。

单条 event row 的 provider-level 规范见：

- [TdxQuant_Provider_Subscription_Event_Contract.md](/opt/iflow/TdxQuant/docs/TdxQuant_Provider_Subscription_Event_Contract.md)

每行当前固定字段：

- `schema_version`
- `capability`
- `run_id`
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

字段语义：

- `session_id`：本次 task run 的稳定会话 id
- `provider_instance_id`：底层 runtime subscription session id
- `subscription_id`：本次订阅注册 id
- `sequence`：单调递增事件序号
- `event_type`：当前第一版固定为 `quote_update`
- `symbol`：归一化后的股票代码；无法识别时可为 `null`
- `source_ts`：从 TongDaXin callback payload 中尽力提取的源时间
- `event_ts`：本地落盘时间
- `reconnect_metadata`：当前第一版固定为空对象
- `payload`：保留序列化后的原始事件载荷

## 5. CSV Contract

任务会同时写一份轻量 CSV，方便人工查看和简单表格处理。

当前行字段至少包括：

- `sequence`
- `symbol`
- `event_type`
- `source_ts`
- `event_ts`
- `session_id`
- `provider_instance_id`
- `subscription_id`
- `payload_json`

它不是主 contract，主 contract 仍以 `JSONL` 为准。

## 6. Status Contract

任务还会维护 `status.json`，用于让外部观察任务状态而不用扫描整份事件流。

当前固定字段至少包括：

- `schema_version`
- `capability`
- `run_id`
- `state`
- `session_id`
- `provider_instance_id`
- `subscription_id`
- `started_at`
- `finished_at`
- `stop_reason`
- `subscribed_symbols`
- `event_count`
- `unique_symbols`
- `unique_symbol_count`
- `last_event_ts`
- `heartbeat_at`
- `last_source_ts`
- `reconnect_count`
- `consecutive_reconnect_failures`
- `last_disconnect_at`
- `last_reconnect_at`
- `next_reconnect_at`
- `degraded_since`
- `last_error`
- `artifacts`

`state` 当前可能值：

- `starting`
- `running`
- `reconnecting`
- `degraded`
- `stopping`
- `completed`
- `interrupted`
- `failed`

`stop_reason` 当前至少可能为：

- `max_events`
- `max_seconds`
- `keyboard_interrupt`
- `subscribe_failed`
- `completed`

在 replay mode 下，当前默认 built-in source 的 completed run 会保留 fixture 自带的 `stop_reason`，例如 `max_events`。

这些 resilience 字段的当前语义为：

- `heartbeat_at`：主循环最近一次确认仍在推进
- `last_event_ts`：最近一次成功落盘 event 的时间
- `last_source_ts`：最近一次上游 event 自带时间
- `reconnect_count`：当前 run 内累计恢复次数
- `consecutive_reconnect_failures`：当前连续恢复失败次数
- `last_disconnect_at`：最近一次确认订阅失效的时间
- `last_reconnect_at`：最近一次恢复成功时间
- `next_reconnect_at`：下一次计划恢复探测时间；在当前 background/bridge terminal persistence 中会清空为 `null`
- `degraded_since`：进入 `degraded` 的时间
- `last_error`：最近一次恢复失败的结构化错误

## 7. Completion Summary

任务结束后返回的 task result 当前至少包含：

- `input`
- `subscription`
- `summary`
- `status`
- `artifacts`
- `subscribe_result`
- `unsubscribe_result`

其中 `artifacts` 会暴露：

- `run_dir`
- `manifest_path`
- `status_path`
- `summary_path`
- `jsonl_output_path`
- `csv_output_path`
- `status_output_path`

同时 canonical run bundle 还会稳定生成：

- `events_jsonl_path`
- `events_csv_path`
- `summary_path`

`summary.json` 当前也会增量补充 resilience 摘要字段：

- `reconnect_count`
- `degraded_duration_ms`
- `final_last_error`

在 replay mode 下，这些 artifact key 当前有稳定 alias 语义：

- `jsonl_output_path == events_jsonl_path`，除非调用方显式传入 legacy `jsonl_output_path`
- `csv_output_path == events_csv_path`，除非调用方显式传入 legacy `csv_output_path`
- `status_output_path == status_path`，除非调用方显式传入 legacy `status_output_path`

也就是说：

- canonical run bundle 始终写到本次新建的 `run_dir`
- legacy `*_output_path` 只是额外镜像出口，不替代 canonical artifact path

## 8. 当前边界

这一版明确只做：

- 前台长驻 task
- 文件协议产物
- bounded run
- `Ctrl+C` 优雅退出
- replay mode completed-run materialization
- built-in replay source 自动选择
- 显式 replay manifest / run-dir 输入

截至 `2026-05-03`，围绕这个前台 task 已经额外形成一层独立 control plane，但它不是 `subscription-watch` 本身的新执行语义：

- worker-local single-active background control
- worker 侧 HTTP bridge：`tdxquant bridge serve --config runtime/bridge/worker-bridge.json`
- Master 侧静态 worker registry + `bridge watch-start|watch-stop|watch-status`
- bridge 只管理 watch lifecycle / artifact 查询，不改变前台 run artifact contract

当前 bridge 暴露的稳定 endpoint 为：

- `POST /bridge/v1/watch/start`
- `POST /bridge/v1/watch/stop`
- `GET /bridge/v1/watch/status`
- `GET /bridge/v1/watch/list`
- `GET /bridge/v1/watch/artifacts`
- `GET /bridge/v1/watch/events`
- `GET /bridge/v1/watch/logs`
- `GET /bridge/v1/health`

bridge 访问前提当前也是 contract 的一部分：

- 请求必须带 `Authorization: Bearer <token>`
- worker 侧会按 `master_allowlist` 做 source-IP allowlist 校验
- 任一前置条件不满足时，bridge 会直接拒绝请求，不进入 watch control 逻辑

## 8.1 Bridge Integration Regression Surface

- worker-local background control 仍是 watch runtime state 的唯一真源
- `GET /bridge/v1/watch/status` 只做 controller 读模型投影，不生成 bridge-only watch state
- `/bridge/v1/health` 以及 active `run_id` fallback 使用 control-only read path，不扫描额外运行态文件来推导 watch state
- Master 侧 registry/client 错误按 transport 语义归类，例如 `invalid JSON`、`connection refused`、`HTTP non-JSON failure`；它们不能被解释为 task runtime failure
- bridge auth / allowlist 拒绝同样属于 transport-scoped failure，不改变 watch runtime state
- CLI `bridge health`、`bridge watch-status`、`bridge watch-list`、`bridge watch-artifacts`、`bridge watch-events`、`bridge watch-logs` 直接输出 Master 侧 client 收到的 JSON payload，不做二次改写

这层 bridge 只做 transport / background-control shell，不重新定义 watch lifecycle。
因此当 live run 从 `watch_status.state=running -> reconnecting -> degraded -> running` 变化时：

- `run_id` 不变
- `events.jsonl` 不轮换
- bridge / background / foreground 读取的是同一份 runtime 状态语义

这里要区分两层状态：

- `control.state` 描述 worker-local background process / control-plane 状态
- `watch_status.state` 描述 `subscription-watch` task 的运行态摘要；`reconnecting` / `degraded` 属于这一层 runtime-state summary

当前 `watch-start` / `watch-status` 还有两条稳定控制面语义：

- `watch-start` 会把 `stock_list`、`max_events`、`max_seconds`、`poll_interval` 以及可选 `idempotency_key` 透传到 worker-local background controller；若请求本身不可能形成有效 run，会在 spawn 前直接返回 `INVALID_REQUEST`
- `watch-start` 在当前 active run 上支持 same-`idempotency_key` replay；同键重试返回同一个 active `run_id`，而不是新的 `ALREADY_RUNNING`
- `watch-status` 只返回当前 controller projection / active snapshot；当前实现会忽略显式 `run_id`，若没有 active watch，则 `watch_status` 明确为 `null`，不会静默回退到历史 `status.json`

截至 `2026-05-03`，bridge 侧这些读取行为也已经有了明确边界：

- worker-local background controller 拥有 `status / list / artifacts / events / logs` 的本地读模型
- bridge 只负责 HTTP transport、`Authorization` / allowlist 校验和结果 envelope 映射；其中 `watch/status` 是 controller 输出的 verbatim projection
- bridge 不再被视为“自行扫描本地文件系统拼装状态”的契约拥有者

这一版明确**不做**：

- reconnect/backoff
- HTTP / SSE 输出通道
- `catalog` / preset 暴露
- live subscription session / delayed playback 模拟

这里的“不做”应理解为：

- `subscription-watch` task 自身仍不是 daemon API
- 后台控制面已经独立存在，但目前只提供单 worker、single-active watch 管理，不扩展为通用多任务调度器

## 9. Replay Failure Behavior

`provider_mode=replay` 下，`subscription-watch` 的失败语义当前是稳定的：

- replay source 缺文件时直接失败，例如缺少 `manifest.json`、`status.json`、`summary.json` 或 `events.jsonl`
- malformed bundle 直接失败，例如内置 bundle 结构不符合 `manifest/status/summary/events` 预期
- 返回值固定为 task `Result` failure，`code=INVALID_REQUEST`
- `data.replay_source.mode` 固定为 `replay`
- `data.replay_source.capability` 固定为 `subscription.watch`
- 不会降级回 live runtime，也不会尝试打开 subscription session

因此上层调用方可以把 replay bundle 问题视为输入合同错误，而不是运行时随机故障。
