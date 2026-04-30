## Context

`TdxApiManager.runtime.open_subscription_session()` 已经解决了 TongDaXin 订阅必须依赖持久 runtime 的底层问题，但当前调用方仍要自己处理：

- session 生命周期
- callback 回调落盘
- 事件序号和摘要统计
- 结束条件
- 产物路径与状态文件

这对于日常使用和上层项目集成都过于原子。与此同时，两个上层项目都已经明确表达了对 `JSONL` 事件流和稳定状态文件的需求，但当前阶段又不适合直接跳到 daemon / HTTP / SSE。这使得“前台长驻 task”成为最合适的过渡形态。

## Goals / Non-Goals

**Goals:**

- 提供稳定的 `TdxTaskManager.subscription_watch(...)` 工作流。
- 提供 `task subscription-watch` CLI 入口。
- 把订阅 callback 归一化成稳定事件行，并持续落到 `JSONL`。
- 提供轻量 `CSV` 平铺视图和 `status.json` 状态文件。
- 支持 `max_events` / `max_seconds` 这类可测试、可自动结束的运行边界。
- 支持 `Ctrl+C` 优雅收尾，并在结果中保留 stop reason、事件计数和产物路径。

**Non-Goals:**

- 不实现后台 daemon。
- 不实现 `start / stop / status / list` 进程控制面。
- 不把 `subscription-watch` 立即纳入 `catalog` 或 task preset。
- 不在本包里引入 HTTP/SSE 服务层。
- 不处理 reconnect/backoff 重连策略。

## Decisions

### 1. `subscription-watch` 建立在现有 runtime subscription session 之上

任务层直接复用 `manager.runtime.open_subscription_session()`，而不是重新实现另一套 runtime lifecycle。

理由：

- 已有 session 已解决单次初始化、多次调用和显式关闭语义。
- 任务层只需要增加 orchestration、artifact 和结束态治理。

备选方案：

- 直接在 task 层重写 `tqcenter` lifecycle  
  否决原因：会重复已存在的 runtime session 逻辑，并增加偏移风险。

### 2. 事件在 callback 内直接落盘，而不是先整体缓存在内存

callback 收到事件后，任务层会立刻：

- 归一化 event row
- append `JSONL`
- append `CSV`
- 更新内存统计
- 重写 `status.json`

理由：

- 更接近真实长期运行语义
- 中途中断时也能保住已经收到的事件
- 适合后续上层直接跟踪文件

备选方案：

- 先积累内存列表，退出时一次性写文件  
  否决原因：长跑任务风险高，且不适合实时消费。

### 3. 第一版提供前台 bounded-run 模式和人工中断模式

第一版同时支持：

- `max_events`
- `max_seconds`
- `Ctrl+C`

主循环只负责保持 session 存活并检查结束条件；真正事件处理交给 callback。

理由：

- `max_events` / `max_seconds` 让测试和自动化调用可控
- `Ctrl+C` 保持人工前台运行体验
- 比直接实现 daemon 控制面简单得多

### 4. 事件 contract 统一为一行一个 normalized event

第一版 JSONL 行固定至少包含：

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

如果单次 callback 携带多个 symbol，任务层会拆成多行事件并各自分配 sequence。

理由：

- 上层更容易做文件消费、回放和 contract test
- 避免把 TongDaXin 原始自由 shape 直接暴露给外部

### 5. 状态文件明确区分运行中和结束态

`status.json` 至少记录：

- `state`
- `started_at`
- `finished_at`
- `stop_reason`
- `subscribed_symbols`
- `event_count`
- `unique_symbols`
- `artifacts`

状态会在：

- 任务启动时
- 每次事件到来后
- 正常结束或异常结束时

被重写。

理由：

- 上层不必实时扫描 JSONL 才能知道任务是否还活着
- 为后续 daemon / status 控制面保留演化路径

## Risks / Trade-offs

- [TongDaXin callback payload shape 可能不稳定] → 先实现保守归一化规则，无法识别时仍保留原始 `payload`。
- [callback 可能来自不同线程] → 使用锁保护 sequence、统计和状态文件写入。
- [频繁重写状态文件有额外 I/O] → 第一版接受这类成本，优先保证可观察性。
- [前台 task 不能替代真正后台服务] → 在文档和 spec 中明确这只是第一阶段入口，不等同 daemon。

## Migration Plan

1. 通过 OpenSpec 固定 `subscription-watch` task contract。
2. 先补 task manager 和 CLI 测试。
3. 实现 callback 归一化、artifact 追加和结束态治理。
4. 更新 task profile 和文档。
5. 通过验证后再决定是否继续上收 daemon。

## Open Questions

- 后续是否需要把 `subscription-watch` 的 JSONL contract 上升为独立 provider-level event contract，并与未来 HTTP/SSE 通道共用同一 schema。
