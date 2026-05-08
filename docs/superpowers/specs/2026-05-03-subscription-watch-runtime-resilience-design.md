# Subscription Watch Runtime Resilience Design

Date: 2026-05-03
Topic: `subscription-watch-runtime-resilience`
Status: Draft for review

## Context

`subscription-watch` 当前已经具备三层基础：

- 前台 run artifact contract
  - `events.jsonl`
  - `status.json`
  - `summary.json`
  - `manifest.json`
- worker-local single-active background control
- worker HTTP bridge + master-side registry/control

这条主线已经能跑，但还没有补齐“长期运行”语义：

- live runtime 断线后的自动恢复
- reconnect / backoff contract
- degraded 运行态
- 更稳定的 heartbeat / watermark / reconnect 摘要
- foreground / background / bridge 共用同一套 runtime 状态模型

当前最需要收口的，不是新 transport，而是 **live `subscription-watch` 的 resilience contract**。

## Goals

- 为 live `subscription-watch` 增加断线自动重连能力。
- 引入稳定的 reconnect / degraded 运行态语义。
- 在不改变 `run_id` 的前提下，记录同一次 run 内的恢复轨迹。
- 扩展 `status.json` / `summary.json`，让 foreground、background、bridge、master 看到同一套 runtime health 信息。
- 保持现有 run artifact contract 和 bridge control plane 的主体结构不变。

## Non-Goals

- 不做 SSE 或新的 transport。
- 不做多 worker 协调或调度。
- 不做新的任务类型。
- 不做分裂式 “一次断线生成一个新 run” 的 lifecycle。
- 第一版不在 `events.jsonl` 中引入 synthetic reconnect lifecycle events。

## Chosen Scope

第一版范围固定为：

- live `subscription-watch` 的自动重连
- bounded reconnect attempts
- 超过阈值后进入 `degraded`
- `degraded` 状态下低频恢复探测
- 恢复成功后回到 `running`
- foreground / background / bridge 共用统一 runtime state contract

不包含：

- replay contract 的重新设计
- bridge 新 endpoint
- worker 自注册
- master 调度逻辑

## Runtime Model

### Same Run Identity

重连前后视为 **同一次 watch run**：

- 保持同一个 `run_id`
- 继续写同一个 `events.jsonl`
- 继续更新同一个 `status.json`
- 最终只生成一份 `summary.json`

这样上层看到的是：

- “一次长期运行里发生过若干次重连”

而不是：

- “每次断线都生成一个新 run”

## State Machine

现有终态保留：

- `completed`
- `interrupted`
- `failed`

运行中状态扩展为：

- `starting`
- `running`
- `reconnecting`
- `degraded`
- `stopping`

### State Meanings

- `starting`
  - session 正在建立，尚未进入稳定订阅
- `running`
  - 正常收事件
- `reconnecting`
  - 已检测到订阅不可用，正在有限次 backoff 重试
- `degraded`
  - 已超过快速重连上限，但进程继续存活，并进入低频恢复探测
- `stopping`
  - 收到 stop / interrupt，正在清理和写终态

### State Transitions

- `starting -> running`
- `starting -> failed`
- `running -> reconnecting`
- `reconnecting -> running`
- `reconnecting -> degraded`
- `degraded -> running`
- `running|reconnecting|degraded -> stopping -> completed|interrupted|failed`

### Background Reconcile Semantics

`subscription_watch_background.reconcile_background_state(...)` 也必须同步扩展为识别：

- `reconnecting`
- `degraded`

第一版约束为：

- `starting / running / reconnecting / degraded / stopping` 都视为 **active-process states**
- 如果 worker 进程在 `starting / running / reconnecting / degraded` 期间丢失：
  - reconcile 必须把状态归一成 `failed`
  - `reason = "stale_process_state"`
- 如果 worker 进程在 `stopping` 期间丢失：
  - reconcile 归一成 `stopped`
- `active.json` 的 `state` 必须与 foreground runner 当前高层状态保持一致，不允许 bridge/background 暴露一套独立状态名

## Recovery Policy

### Fast Reconnect Phase

当 `running` 状态下检测到 session 失效或订阅调用失败时：

- 切换到 `reconnecting`
- 按短 backoff 重试
- 记录连续失败次数
- 当达到快速重连上限后，不直接退出，而是进入 `degraded`

第一版策略方向：

- 有上限快速重试
- 不做无限高频自旋
- v1 默认：
  - 最多 `3` 次快速重连
  - backoff 间隔依次为 `1s`、`2s`、`5s`
  - 第 `3` 次仍失败则进入 `degraded`

### Degraded Phase

进入 `degraded` 后：

- 进程继续存活
- bridge 和本地状态读取仍可见
- 不再高频重试
- 切换到低频恢复探测

这意味着：

- worker 仍“在线”
- 但订阅当前不可用
- master 可以看到最近错误、重连次数、当前健康状态

### Recovery from Degraded

`degraded` 不是终态。

系统会继续做低频恢复探测，例如：

- 每 `60s` 再试一次恢复订阅

一旦恢复成功：

- 状态回到 `running`
- 同一次 `run_id` 继续推进

第一版不设置“持续 degraded 多久后永久放弃”的总时长上限；进程会继续存活并低频探测，直到：

- 恢复成功
- 收到显式 stop
- 或 runner 自身进入不可恢复失败

### Disconnect Detection

第一版不把“长时间没有新行情事件”本身视为断线。

进入 `reconnecting` 的条件只包括：

- provider subscription 调用抛出异常
- session read / poll 调用返回显式失败
- runtime 明确给出 session 已失效 / 已关闭信号

`heartbeat_at` 只表示 runner 主循环仍在推进，不承担 provider-level disconnect 判定职责。

## Runtime Status Contract

第一版建议在现有 `status.json` 基础上**增量**补这些字段：

- `heartbeat_at`
- `last_event_ts`
- `last_source_ts`
- `reconnect_count`
- `consecutive_reconnect_failures`
- `last_disconnect_at`
- `last_reconnect_at`
- `next_reconnect_at`
- `degraded_since`
- `last_error`

### Field Semantics

- `heartbeat_at`
  - runner 最近一次确认自己仍在推进主循环的时间
- `last_event_ts`
  - 最近一次成功落盘事件时间
- `last_source_ts`
  - 最近一次上游事件自带时间
- `reconnect_count`
  - 当前 run 累计发生过的重连次数
- `consecutive_reconnect_failures`
  - 当前连续恢复失败次数
- `last_disconnect_at`
  - 最近一次确认断线的时间
- `last_reconnect_at`
  - 最近一次恢复成功时间
- `next_reconnect_at`
  - 下一次计划恢复探测时间
- `degraded_since`
  - 进入 `degraded` 的时间
- `last_error`
  - 结构化对象，至少含 `code` / `message` / `at`

这里不新增独立 `runtime_health` 字段。第一版直接使用 `state` 表示运行态：

- `running`
- `reconnecting`
- `degraded`

避免和现有 `state` 形成一套 1:1 镜像字段。

## Summary Contract

`summary.json` 不记录完整恢复轨迹，只记录最终摘要，建议新增：

- `reconnect_count`
- `degraded_duration_ms`
- `final_last_error`

其中 `degraded_duration_ms` 采用**累计语义**：

- 同一次 run 内如果发生多次 `degraded -> running -> degraded`
- 最终 `summary.json` 记录所有 degraded 区间的总时长

这样：

- `status.json` 负责运行中观察
- `summary.json` 负责结束后复盘

### Event Row Contract

第一版仍然不在 `events.jsonl` 中引入 synthetic reconnect lifecycle events。

同时，`subscription_event.reconnect_metadata` 在 v1 继续保持：

- 默认 `{}` 
- 不因重连成功而给普通行情事件补写 reconnect 元数据

reconnect 轨迹只通过：

- `status.json`
- `summary.json`
- `runner.log`

来表达。

## Layer Boundaries

### Foreground Task

foreground `subscription-watch` 负责：

- live subscription session lifecycle
- reconnect/backoff loop
- artifact 写入
- runtime status 更新

### Background Control

background control 不重新发明 resilience 逻辑，只负责：

- start / stop / status / list / artifacts / events / logs
- 暴露和保存 foreground runner 的 runtime state

`stopping` 由 background control 或 foreground interrupt 驱动，不是 reconnect loop 自发进入的健康状态。

### Bridge

bridge 继续只做 transport shell：

- HTTP envelope
- token / allowlist
- 调用 background controller 的读写模型

bridge 不持有独立的 reconnect 逻辑。

## Error Handling

第一版要区分三类问题：

1. 启动失败
   - `starting -> failed`
2. 运行中断线但可恢复
   - `running -> reconnecting -> running`
3. 运行中断线且超过快速恢复上限
   - `running -> reconnecting -> degraded`

### Stop Cleanup Requirements

当 `reconnecting` 或 `degraded` 状态收到 stop 信号时：

- 必须取消待执行的 reconnect / probe 等待
- 状态切换到 `stopping`
- `next_reconnect_at` 清空为 `null`
- 最终按现有终态 contract 写出 `completed` / `interrupted` / `failed`

## Fixture Impact

这条 change 不要求重写现有已完成态 fixture 的 schema 版本，但会新增 resilience representative fixtures。

第一版约束为：

- 现有 `subscription-watch-status-completed`
- 现有 `subscription-watch-summary-completed`

仍然保持有效；新增字段对旧 fixture 采用可选扩展。

同时补新增量 fixture，例如：

- `subscription-watch-status-reconnecting`
- `subscription-watch-status-degraded`
- `subscription-watch-summary-with-reconnect`

用于锁定新的 runtime contract。

关键原则：

- 不把短暂断线直接升级成终止性失败
- 不把长期不可用伪装成正常 `running`
- 不让失败恢复路径静默丢失可观察性

## Testing Focus

第一版测试应覆盖：

- `running -> reconnecting -> running`
- `running -> reconnecting -> degraded`
- `degraded -> running`
- bounded retry 上限
- low-frequency degraded probe
- 同一 `run_id` 下连续重连
- `status.json` 的新字段更新
- `summary.json` 的最终 resilience 摘要
- background / bridge 读取到一致的 runtime state

## Open Question

当前仍有一个待确认点：

- 是否要在 `events.jsonl` 中加入 synthetic reconnect lifecycle events，例如：
  - `reconnect_started`
  - `reconnect_succeeded`
  - `degraded_entered`

当前推荐：**第一版不要**。  
先把这些信息固定在：

- `status.json`
- `summary.json`
- `runner.log`

如果后续上层确实需要事件流级别的恢复轨迹，再单独补一条 change。

## Recommended Next Step

如果这份设计认可，下一步应进入 implementation plan，拆成：

1. runner resilience loop
2. status/summary schema extension
3. background read-model alignment
4. bridge regression coverage
