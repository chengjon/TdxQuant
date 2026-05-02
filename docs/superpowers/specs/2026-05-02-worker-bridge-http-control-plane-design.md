# Worker Bridge HTTP Control Plane Design

## Context

当前 `subscription-watch` 已经具备稳定的前台 run artifact contract：

- `events.jsonl`
- `status.json`
- `summary.json`
- `manifest.json`

同时，CLI subprocess replay 和 fake provider mode 也已经收口，说明 `subscription-watch` 这条线已经有了比较清晰的 provider/task contract。现在缺的不是单次执行能力，而是 **多台固定 worker 的后台控制面**。

目标运行形态是：

- 多台固定 worker 机器，各自运行 `TDX + tdxquant`
- 每台 worker 只负责本机任务
- 只有一台固定 Master 机器负责查看和控制这些 worker
- worker 之间不互控，也不做主控竞争

这意味着问题已经从“本机后台 task”升级成“**中心主控 + 多 worker 远程控制**”，但又不需要引入分布式选主、租约竞争或脑裂处理。

## Goals

- 为每台 worker 提供稳定的本地 `subscription-watch` 后台控制 contract。
- 提供 `tdxquant bridge serve` 形式的 worker HTTP bridge。
- 让 Master 通过局域网 HTTP 调用固定 worker 的 bridge，实现：
  - `start`
  - `stop`
  - `status`
  - `list`
  - `artifacts/logs`
  - `health`
- 第一版只管理 `subscription-watch` 后台任务。
- 第一版采用：
  - Master 静态 worker 清单
  - 静态 token
  - source allowlist
  - 每个 worker 单活后台 watch

## Non-Goals

- 不支持 trade 远控。
- 不支持 block write 远控。
- 不支持 worker 自注册。
- 不支持多 Master。
- 不支持 worker 间互控。
- 不支持同一 worker 上多个并发后台 watch。
- 不做分布式锁、选主、租约、脑裂恢复。
- 不做完整用户/角色系统。
- 不做通用任务编排平台。
- 不做 HTTP artifact 文件代理下载，第一版只返回路径和摘要。

## Approaches Considered

### Option A: Worker bridge 直接包装现有 task CLI

Worker bridge 收到 HTTP 请求后，直接后台启动/停止 `tdxquant task subscription-watch`，状态依赖 pid file 与 run dir 推断。

优点：

- 最快落地
- 最大化复用现有 CLI

缺点：

- lifecycle 语义会分散在 bridge 和 CLI 之间
- `status/list/stop` 语义容易变脆
- 后续扩能力时会堆很多包装分支

### Option B: 本地后台控制层 + HTTP bridge

先做 worker-local `subscription-watch background control`，再让 `bridge serve` 调这层。

优点：

- 本地控制与远程控制共享同一套 contract
- 状态机、锁、artifact discovery 只实现一次
- 以后可以同时支持本地 CLI 控制和远程 HTTP 控制

缺点：

- 初始工作量更高
- 需要先定义 worker 本地后台 contract

### Option C: bridge 内部自带后台调度，不单独抽本地控制层

只有 `bridge serve` 能管理后台 watch，本地不暴露统一控制层。

优点：

- 对 Master 控 worker 场景最直接

缺点：

- 本地排障与远控 contract 割裂
- 以后补本地控制时容易重复实现

## Recommended Approach

采用 **Option B: 本地后台控制层 + HTTP bridge**。

原因：

- 当前目标不是一次性远控脚本，而是可长期演进的 worker control plane。
- Master、worker 本地 CLI、后续其他 transport 都应该共享同一套后台控制 contract。
- 这样 bridge 只是 transport shell，不会演变成第二套业务控制器。

## Architecture

设计拆成 3 层。

### 1. Worker Local Background Control

这是 worker 本地单机控制层，只管理一个后台 `subscription-watch`。

职责：

- `start`
- `stop`
- `status`
- `list`
- `artifacts/logs`
- 管理 `pid` / `lock` / `active.json` / `run_dir`

第一版语义：

- 单 worker 同时最多 1 个活跃后台 watch
- `start` 时如果已有活跃任务，稳定拒绝
- `stop` / `status` / `list` 都不需要任务名

本地持久化至少包括：

- `active.json`
- `pid`
- `lock`
- canonical run artifact bundle：
  - `manifest.json`
  - `status.json`
  - `summary.json`
  - `events.jsonl`
  - `events.csv`

建议状态机：

- `starting`
- `running`
- `stopping`
- `completed`
- `failed`
- `stopped`

### 2. Worker HTTP Bridge

bridge 作为 `tdxquant bridge serve` 常驻运行，不单独拆包。

职责：

- 接受 Master HTTP 请求
- 做 token 校验和 source allowlist
- 调用 worker 本地后台控制层
- 返回稳定 JSON result

bridge 不直接重新定义 `subscription-watch` 的业务语义，只包装控制语义。

### 3. Master Registry / Controller

Master 维护静态 worker 清单，并主动调用每台 worker bridge。

每个 worker 配置至少包括：

- `worker_id`
- `label`
- `host`
- `port`
- `token_ref`
- `role_tags`
- `enabled`

Master 第一版职责：

- 聚合 worker `health`
- 聚合 worker `status`
- 对指定 worker 发 `start`
- 对指定 worker 发 `stop`
- 查看 active / last_completed / last_failed

Master 第一版不做：

- 自动发现
- worker 自注册
- 自动调度
- 跨 worker 容错切换

## HTTP Contract

第一版只暴露 6 个 endpoint。

- `POST /bridge/v1/watch/start`
- `POST /bridge/v1/watch/stop`
- `GET /bridge/v1/watch/status`
- `GET /bridge/v1/watch/list`
- `GET /bridge/v1/watch/artifacts`
- `GET /bridge/v1/health`

### `POST /bridge/v1/watch/start`

输入：

- `stock_list`
- `max_events`
- `max_seconds`
- `poll_interval`
- 可选 `run_root_dir`

返回：

- 成功：`started`
- 已有活跃任务：稳定失败 `already_running`

### `POST /bridge/v1/watch/stop`

输入：

- 可选 `reason`

返回：

- 成功停止：`stopped`
- 没有活跃任务：建议 `noop`

### `GET /bridge/v1/watch/status`

返回当前 active task 状态快照。

若无 active task：

- 返回明确空状态
- 不作为 transport 错误

### `GET /bridge/v1/watch/list`

第一版只返回：

- `active`
- `last_completed`
- `last_failed`

不做完整历史分页。

### `GET /bridge/v1/watch/artifacts`

返回当前 active 或最近一次任务的 artifact 路径与摘要：

- `run_dir`
- `manifest_path`
- `status_path`
- `summary_path`
- `events_jsonl_path`
- `events_csv_path`

第一版不直接返回文件内容。

### `GET /bridge/v1/health`

返回：

- bridge 在线状态
- 版本
- worker 标识
- 本地后台控制层可用性

## Security Model

第一版采用最小安全边界：

- `Authorization: Bearer <token>`
- worker 侧 source allowlist
- 仅允许固定 Master 来源访问

这比用户系统、角色系统、双向 TLS 或 OAuth 简单得多，适合固定局域网环境。

限制：

- 这是“受控局域网最低可用安全边界”，不是面向公网的安全模型
- 第一版不解决 token 轮换、细粒度权限和多租户问题

## Control and Artifact Semantics

Master 应把 bridge 返回的内容视为控制结果，不直接假定 worker 本地文件布局。

关键原则：

- canonical run artifact 仍然由 worker 本地 `subscription-watch` contract 定义
- bridge 只暴露可消费的路径和摘要
- Master 不通过共享文件系统直接读 worker 文件

因此，第一版“查看 artifacts”本质上是：

- 先拿到路径和元数据
- 再由后续能力决定是否做代理下载或集中同步

## Failure Model

需要优先稳定以下失败类型：

- `already_running`
- `not_running`
- `invalid_request`
- `unauthorized`
- `forbidden_source`
- `worker_unhealthy`
- `start_failed`
- `stop_failed`

其中：

- `status` 不应因为“当前没有 active task”就报 transport failure
- `list` 也不应因为“没有历史任务”就失败

## Risks / Trade-offs

- **[Risk] 只做单活后台 watch，后续多任务能力需要重新扩展。**
  - Mitigation: 第一版明确把 contract 建在 `single active watch` 上，后续若扩多实例，再引入实例名和实例索引。

- **[Risk] 静态 worker registry 在机器增减时需要手工维护。**
  - Mitigation: 第一版用静态配置换取最低复杂度；后续如有必要再做注册协议。

- **[Risk] HTTP bridge 如果直接操纵底层文件，会导致状态和任务 contract 偏脆。**
  - Mitigation: 通过 worker-local background control 层统一 lifecycle 和 artifact 语义。

- **[Trade-off] 第一版不代理 artifact 文件内容，只返回路径和摘要。**
  - Mitigation: 先把控制面做稳；真正的 artifact download/sync 单独立项。

- **[Trade-off] 第一版只用静态 token + allowlist。**
  - Mitigation: 这足够覆盖固定 Master + 固定 worker 的局域网场景，但不作为公网安全方案。

## Rollout Strategy

建议按 3 步落地：

1. 先实现 worker-local `subscription-watch background control`
2. 再实现 `tdxquant bridge serve` 和 HTTP contract
3. 最后实现 Master 静态 registry 与聚合控制 CLI/UI

这样每一层都可以独立验证：

- 本地单机生命周期
- 单个 worker 远控
- 多 worker 聚合控制

## Open Questions

- 第一版 Master 是 CLI 形态还是单独的本地面板/服务形态？
- `artifacts/logs` 第二版是否需要支持文件内容拉取，而不只是路径与摘要？
- `health` 是否要纳入 worker 上 `runtime.health` 的摘要，而不只是 bridge 自身在线状态？
