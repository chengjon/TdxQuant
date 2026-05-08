## Context

`subscription-watch` 已经拥有：

- foreground run artifact contract
- background single-active control
- bridge HTTP transport shell

但 live watch 目前仍是“一次 subscribe 后简单 sleep 等边界条件”，没有显式 reconnect lifecycle，也没有把 `reconnecting / degraded` 作为 background/bridge 可见状态。

## Decisions

### 1. 断线恢复保留同一 `run_id`

第一版 resilience 不把断线视为新 run。重连前后：

- 保持同一个 `run_id`
- 继续写同一个 `events.jsonl`
- 继续更新同一个 `status.json`
- 最终只生成一份 `summary.json`

### 2. 运行态扩展为 `running / reconnecting / degraded`

foreground task 在现有终态之外新增：

- `reconnecting`
- `degraded`

语义：

- `reconnecting`：快速、有限次恢复尝试
- `degraded`：超过快速重连上限后继续存活，并按低频 probe 尝试恢复

第一版默认：

- 快速 backoff：`1s / 2s / 5s`
- 低频 degraded probe：`60s`

### 3. 不新增 synthetic reconnect lifecycle events

第一版不在 `events.jsonl` 里写 `reconnect_started` / `reconnect_succeeded` / `degraded_entered` 之类事件。

reconnect 轨迹通过：

- `status.json`
- `summary.json`
- `runner.log`

表达即可。普通事件行里的 `reconnect_metadata` 在 v1 继续保持 `{}`。

### 4. 复用现有 `last_event_ts`，不新增镜像健康字段

为避免 contract 分裂：

- 继续使用 `last_event_ts`
- 不重新引入 `last_event_at`
- 不新增与 `state` 1:1 镜像的 `runtime_health`

运行态由 `state` 直接表达。

### 5. Background reconcile 必须识别 resilience active states

`subscription_watch_background.reconcile_background_state(...)` 需要把：

- `starting`
- `running`
- `reconnecting`
- `degraded`
- `stopping`

统一视为 active-process states。

其中：

- `starting / running / reconnecting / degraded` 期间 pid 丢失 => `failed(stale_process_state)`
- `stopping` 期间 pid 丢失 => `stopped`

### 6. 终态必须清理过期的 `next_reconnect_at`

一旦 run 进入：

- `completed`
- `interrupted`
- `failed`

终态 status 中的 `next_reconnect_at` 必须清空为 `null`，避免保留一个不会到来的 probe 时间。

## Contract Surface

### `status.json` 新增字段

- `heartbeat_at`
- `last_source_ts`
- `reconnect_count`
- `consecutive_reconnect_failures`
- `last_disconnect_at`
- `last_reconnect_at`
- `next_reconnect_at`
- `degraded_since`
- `last_error`

### `summary.json` 新增字段

- `reconnect_count`
- `degraded_duration_ms`
- `final_last_error`

其中 `degraded_duration_ms` 采用累计语义：同一 run 内多次进入 degraded 时，最终汇总所有 degraded 区间时长。

## Risks / Trade-offs

- [当前 runtime session 没有专用 poll API] → 第一版通过 `get_subscribe_hq_stock_list()` 做 liveness probe，而不是发明新 transport。
- [bridge/background 可能保留 zombie state] → 将 `reconnecting / degraded` 纳入 active-process reconcile 语义，并用 focused tests 锁定。
- [fixture 漂移] → 新增 representative reconnecting/degraded/summary fixtures，同时保持旧 completed fixtures 继续有效。

## Migration Plan

1. 扩展 run artifact builders。
2. 在 foreground task 中加入 bounded reconnect + degraded probe。
3. 对齐 background reconcile 与 runner terminal cleanup。
4. 补 resilience fixtures、docs、focused regression。

回滚策略：

- 若 reconnect loop 引发回归，可回退到无 resilience 的 live foreground loop。
- background/bridge 仍然依赖同一 run artifact contract，因此回滚不需要迁移文件结构。
