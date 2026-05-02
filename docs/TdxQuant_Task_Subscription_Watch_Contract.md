# TdxQuant Task Subscription Watch Contract

本文定义前台长驻 `subscription-watch` task 的当前 contract。

它关注的是 task lifecycle、artifact 和运行状态。

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

## 3. 输入参数

当前稳定输入至少包括：

- `stock_list`
- `max_events`
- `max_seconds`
- `poll_interval`
- `jsonl_output_path`
- `csv_output_path`
- `status_output_path`

语义说明：

- `stock_list`：必填订阅股票列表
- `max_events`：达到事件数后自动结束
- `max_seconds`：达到运行时长后自动结束
- `poll_interval`：前台保活轮询间隔
- 若不提供任何自动结束条件，则任务会一直运行到 `Ctrl+C`

## 4. 事件 JSONL Contract

`JSONL` 文件一行一个 normalized event。

单条 event row 的 provider-level 规范见：

- [TdxQuant_Provider_Subscription_Event_Contract.md](/opt/iflow/TdxQuant/docs/TdxQuant_Provider_Subscription_Event_Contract.md)

每行当前固定字段：

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

字段语义：

- `session_id`：本次 task run 的稳定会话 id
- `provider_instance_id`：底层 runtime subscription session id
- `subscription_id`：本次订阅注册 id
- `sequence`：单调递增事件序号
- `event_type`：当前第一版固定为 `quote_update`
- `symbol`：归一化后的股票代码；无法识别时可为 `null`
- `source_ts`：从 TongDaXin callback payload 中尽力提取的源时间
- `event_ts`：本地落盘时间
- `reconnect_metadata`：当前第一版固定为 `null`
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
- `last_event_at`
- `artifacts`

`state` 当前可能值：

- `starting`
- `running`
- `completed`
- `interrupted`
- `failed`

`stop_reason` 当前至少可能为：

- `max_events`
- `max_seconds`
- `keyboard_interrupt`
- `subscribe_failed`
- `completed`

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

- `jsonl_output_path`
- `csv_output_path`
- `status_output_path`

## 8. 当前边界

这一版明确只做：

- 前台长驻 task
- 文件协议产物
- bounded run
- `Ctrl+C` 优雅退出

这一版明确**不做**：

- daemon
- `start / stop / status / list` 控制面
- reconnect/backoff
- HTTP / SSE 输出通道
- `catalog` / preset 暴露
