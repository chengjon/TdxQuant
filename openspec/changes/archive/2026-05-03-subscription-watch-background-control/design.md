## Context

`subscription-watch` 当前已经具备两层稳定能力：

- 前台 task run artifact contract：
  - `manifest.json`
  - `status.json`
  - `summary.json`
  - `events.jsonl`
  - `events.csv`
- worker 侧 HTTP bridge：
  - `watch/start`
  - `watch/stop`
  - `watch/status`
  - `watch/list`
  - `watch/artifacts`
  - `watch/events`
  - `watch/logs`

但 worker-local background control 还没有独立 OpenSpec capability。当前实现里，`SubscriptionWatchBackgroundController` 主要负责 `start/stop`，而 `status/list/artifacts/events/logs` 的多数读取语义仍散落在 `bridge_http.py`。这使得 bridge 不只是 transport shell，也在承担一部分本地 control contract。

这条 change 的目标不是重做 bridge，而是把现有 worker-local control 层正式化，并把剩余的读模型边界收回 background control 模块。

## Goals / Non-Goals

**Goals:**

- 为 worker-local single-active `subscription-watch` 后台控制建立独立 capability spec。
- 固定 background control 的状态模型、stale reconciliation 和 same-`idempotency_key` replay 语义。
- 为 `status/list/artifacts/events/logs` 建立稳定的本地读模型，让 bridge 只负责 HTTP envelope、鉴权和 transport-level error mapping。
- 明确 background control 与 canonical run artifact bundle 的关系，避免形成第二套后台专属 artifact contract。

**Non-Goals:**

- 不新增 bridge endpoint。
- 不改 Master registry / remote control CLI。
- 不扩展到多活 watch、多 worker 调度、trade 远控或 block 远控。
- 不修改 foreground `subscription-watch` 的 canonical run artifact 格式。
- 不引入新的 daemon 机制或外部依赖。

## Decisions

### 1. 背景控制作为独立 capability，而不是修改 foreground task spec

`subscription-watch` foreground task 已经有稳定 run artifact contract。background control 是基于这套 contract 做单活 lifecycle 和诊断读取，不应该反向改变 foreground task 本身的执行语义。

因此本 change 新增独立 capability：

- `tdx-task-subscription-watch-background-control`

而不是继续把后台控制规则塞进 `tdx-task-subscription-watch` 主 spec。

### 2. `SubscriptionWatchBackgroundController` 成为 worker-local control 的唯一语义拥有者

当前 `bridge_http.py` 里已经包含：

- active state 读取
- run status 读取
- active / last_completed / last_failed 扫描
- artifact path 组装
- events/logs tail 读取

这些都属于 worker-local control read model，而不是 HTTP transport 逻辑。实现上应把这些读取能力提升为 background control 模块的稳定 helper 或 controller method，由 bridge 负责调用。

这样可以把 contract 聚焦为两层：

- background control：本地 lifecycle + read models
- bridge：HTTP transport + auth + envelope

### 3. single-active 语义继续保留，并以文件状态 + pid reconciliation 为准

worker-local background control 继续只允许一个活跃 watch：

- `starting`
- `running`
- `stopping`

遇到这些状态时：

- same-`idempotency_key` start 重试返回同一 active run
- 不同请求返回 `ALREADY_RUNNING`

状态合法性不能只依赖 `active.json`；必须结合：

- `pid`
- 进程存活性
- run artifact 终态

做 stale reconciliation。这部分已经有实现基础，应提升为明确 contract，而不是 bridge 假定行为。

`start` 的启动窗口也属于这条 contract 的一部分。若 runner 在 `start_timeout_seconds` 内没有从 `starting` 进入可接受终态，background control 必须返回稳定失败，而不是把“未知是否卡死”的 `starting` 状态伪装成成功。

### 4. 诊断读取继续复用 canonical run artifacts，不派生新的后台专属格式

background control 的 `status/list/artifacts/events/logs` 都必须基于 canonical run artifact bundle：

- `manifest.json`
- `status.json`
- `summary.json`
- `events.jsonl`
- `events.csv`
- `runner.log`

不新增第二套后台专属事件流或状态文件。这样 foreground、background、bridge 共享同一套 run directory contract。

这里要明确两层 schema 的边界：

- `events.jsonl` 单行事件遵循 provider-level subscription event contract
- `manifest.json` / `status.json` / `summary.json` 遵循 run-level task artifact contract

它们可以独立演进版本号；background control 只要求两层 contract 都稳定可读，不要求把它们强行合并成同一 schema version。

### 5. `status` 和 `list` 维持 active-first 视图，而不是历史索引器

第一版 background control 继续保持轻量：

- `status`：只返回当前 active snapshot；若无 active run，则显式返回空状态
- `list`：只返回：
  - `active`
  - `last_completed`
  - `last_failed`

不在这条 change 里扩成完整分页历史索引器。

## Risks / Trade-offs

- [Bridge 与 controller 读模型重叠] → 将 `status/list/artifacts/events/logs` 读取下沉到 background control，bridge 只保留 HTTP 映射。
- [stale process state 容易漂移] → 将 pid 校验、terminal normalization 和 active/no-active 语义写入 spec，并用 focused tests 锁定。
- [foreground/background contract 混淆] → 保持 foreground task spec 不变，明确 background control 只是消费 canonical run artifact。
- [first version 历史视图较弱] → 明确 `list` 只覆盖 `active/last_completed/last_failed`，把完整历史检索留到后续 change。

## Migration Plan

1. 保持现有 bridge endpoint 和 request/response envelope 不变。
2. 将 bridge 当前直接读取文件的逻辑收敛到 background control 模块。
3. 为 controller 增加稳定读模型后，bridge 改为调用 controller，而不是自行拼装本地状态。
4. 更新 task/bridge 文档，使其引用新的 background control capability。
5. 通过 focused bridge/background tests 验证行为未回退，再补 broader regression。

回滚策略：

- 若读模型抽取导致 bridge 回归，可回退到原有 bridge 直接读取文件逻辑。
- canonical run artifact contract 不变，因此回滚不会破坏既有 run directory。

## Open Questions

- 无。第一版范围已限定为 worker-local single-active background control contract completion。
