# TdxQuant Provider Subscription Event Contract

本文定义 TongDaXin 订阅更新的 provider-level normalized event row contract。

它描述的是“一条事件行长什么样”，而不是某个具体 transport。

适用范围：

- `subscription-watch` 的 `JSONL` 事件流
- 未来可能的 HTTP / SSE / replay 通道

不直接定义：

- 前台 task 生命周期
- `status.json`
- daemon 控制面

这些运行期治理内容仍由 task 或 future worker contract 负责。

## 1. Contract Goal

上层系统需要一个稳定的、transport-independent 的事件行 schema，用来消费 TongDaXin 订阅更新，而不必依赖：

- TongDaXin 原始 callback 自由形状
- 当前 task 的实现细节
- 未来具体通过文件、HTTP 还是 SSE 传递

因此，这份 contract 只关心 normalized event row。

## 2. Current Fields

当前每一条 normalized event row 固定至少包含：

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

## 3. Field Semantics

- `schema_version`：当前事件行 schema 版本
- `session_id`：本次上层 watch run 的逻辑会话 id
- `provider_instance_id`：底层 runtime subscription session id
- `subscription_id`：当前订阅注册 id
- `sequence`：单调递增事件序号
- `event_type`：当前第一版固定为 `quote_update`
- `symbol`：归一化股票代码；无法识别时允许为 `null`
- `source_ts`：从原始 callback payload 中尽力提取的源时间
- `event_ts`：事件被 provider 归一化并发出的时间
- `reconnect_metadata`：当前第一版固定为 `null`
- `payload`：保留序列化后的原始 callback 载荷

## 4. Normalization Rules

当前 provider 会优先尝试这几类归一化：

1. symbol-keyed payload
   例如：
   - `{ "600519.SH": {...}, "000001.SZ": {...} }`
   - 会拆成多条事件行

2. explicit symbol payload
   例如：
   - `{ "symbol": "688318.SH", ... }`
   - 会直接生成一条事件行

3. list payload
   例如：
   - `[{...}, {...}]`
   - 会逐条生成事件行

4. unstructured payload
   - 仍会生成事件行
   - `symbol` 允许为 `null`
   - `payload` 保留原始序列化结果

## 5. Source Timestamp Extraction

当前 `source_ts` 会优先尝试从以下字段提取：

- `source_ts`
- `UpdateTime`
- `update_time`
- `DateTime`
- `datetime`
- `time`
- `Time`
- `timestamp`

如果都不存在，则允许为 `null`。

## 6. Example

示例 event row：

```json
{
  "schema_version": "2026-04-28",
  "session_id": "watch-run-001",
  "provider_instance_id": "provider-session-001",
  "subscription_id": "sub-001",
  "sequence": 1,
  "event_type": "quote_update",
  "symbol": "600519.SH",
  "source_ts": "2026-04-28T09:30:01+08:00",
  "event_ts": "2026-04-28T01:30:01.123456+00:00",
  "reconnect_metadata": null,
  "payload": {
    "Now": 123.45,
    "UpdateTime": "2026-04-28T09:30:01+08:00"
  }
}
```

## 7. Relationship To Task Contract

`subscription-watch` task 当前只是这个 event row contract 的一个 delivery channel。

相关 task lifecycle、artifact 和状态文件说明见：

- [TdxQuant_Task_Subscription_Watch_Contract.md](/opt/iflow/TdxQuant/docs/TdxQuant_Task_Subscription_Watch_Contract.md)

## 8. Current Boundary

当前已经稳定的是：

- event row 字段集合
- 基本归一化规则
- 对原始 `payload` 的保留策略

当前尚未稳定的是：

- reconnect metadata 细化结构
- transport-specific wrapper
- HTTP / SSE 推送语义
