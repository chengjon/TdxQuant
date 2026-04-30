## Context

当前 `subscription-watch` 已经是一个可运行的前台订阅 workflow，并且会输出：

- `events.jsonl`
- `events.csv`
- `status.json`

其中最关键的是 `JSONL` 事件行，因为它最接近未来上层项目真正会长期依赖的 machine contract。问题在于，这些字段现在仍然：

- 主要定义在 task 文档里
- 由 `tdxquant/api/task.py` 自己直接拼装
- 没有独立 contract helper 可复用

如果后续继续推进：

- provider-level 订阅事件 contract
- HTTP/SSE 通道
- replay/fake fixture

那么当前形态会造成 schema 重复实现和边界漂移。

## Goals / Non-Goals

**Goals:**

- 定义独立的 provider-level 订阅事件 contract。
- 提供共享的事件归一化 helper。
- 让 `subscription-watch` 显式依赖这个共享 helper，而不是本地拼 schema。
- 为未来 HTTP/SSE/replay 复用同一事件行 schema 打基础。

**Non-Goals:**

- 不新增 HTTP 服务层。
- 不新增 SSE 通道。
- 不新增 daemon 控制面。
- 不改变当前 `subscription-watch` 的 CLI 入口。
- 不引入新的 capability discovery runtime endpoint。

## Decisions

### 1. 以“event row contract”而不是“task contract”作为正式边界

正式 contract 只定义“一行事件长什么样”，而不是把整个 task 运行过程都上提成 provider 级 schema。

理由：

- 上层系统最关心的是事件消费边界
- task lifecycle 仍然属于 task 层
- HTTP/SSE/replay 未来都可以复用同一行 schema

### 2. 提取共享 helper，而不是只补文档

本包不仅补 spec/doc，还会把归一化逻辑提取到独立模块，例如：

- symbol 提取
- source timestamp 提取
- raw callback payload 到 normalized event row 的转换

理由：

- 避免 task 和未来 transport 重复实现
- 测试可以直接锁定 helper 行为

### 3. 保持当前事件字段兼容，不引入破坏性重命名

第一版 provider event contract 直接沿用当前 `subscription-watch` 已经写出的关键字段：

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

理由：

- 当前 task 已经对这些字段做了测试和文档化
- 继续沿用可以避免无意义 breaking change

### 4. 继续允许无法完全识别的原始 payload 进入 `payload`

如果 callback shape 不完全符合已知模式，helper 仍然会：

- 保留序列化后的原始 `payload`
- 尽力提取 `symbol` / `source_ts`

理由：

- TongDaXin callback 形状可能存在环境差异
- 先保证 contract 稳定，再逐步增强识别规则

## Risks / Trade-offs

- [shared helper 与 task 输出可能发生偏差] → 用独立 helper 测试和 task 集成测试同时锁定。
- [现在 formalize 的字段未来仍可能扩展] → 先保证新增字段向后兼容，不轻易改名或删字段。
- [没有 discovery endpoint 暴露事件 contract] → 当前先通过文档/spec 固定边界，后续再决定是否需要 runtime self-description。

## Migration Plan

1. 新增 provider-level subscription event contract spec。
2. 提取共享 helper 并让 task 复用。
3. 更新 task spec 和文档引用。
4. 在现有测试基础上补 shared helper 测试。
5. 通过验证后归档。

## Open Questions

- 未来 HTTP/SSE 通道是否直接复用相同 event row，不再增加 transport-specific wrapper。
