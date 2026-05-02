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
- 不做按 `run_id` 的完整历史 artifact 浏览 API；第一版只覆盖 active / last_completed / last_failed 的控制与诊断路径。

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

第一版必须补一张明确的状态转换矩阵：

| Current | Trigger | Next | Notes |
| --- | --- | --- | --- |
| `starting` | child process healthy and status file advancing | `running` | happy path |
| `starting` | start timeout | `failed` | `start_failed_timeout` |
| `starting` | child process exits unexpectedly | `failed` | `start_failed_process_exit` |
| `running` | natural completion | `completed` | bounded run reached |
| `running` | operator stop | `stopping` | begin graceful stop |
| `running` | child process exits unexpectedly | `failed` | `worker_process_crashed` |
| `stopping` | process exits within grace period | `stopped` | operator initiated |
| `stopping` | grace timeout, forced kill succeeds | `stopped` | `forced_stop` |
| `stopping` | grace timeout, forced kill fails | `failed` | `stop_failed_timeout` |
| `failed` | fresh start request | `starting` | allowed after cleanup |
| `completed` | fresh start request | `starting` | allowed after cleanup |
| `stopped` | fresh start request | `starting` | allowed after cleanup |

补充语义：

- 第一版不允许 `completed` / `failed` / `stopped` 直接复用旧 run，而是每次 fresh start 都创建新 `run_id`
- `starting` 与 `stopping` 都必须有超时阈值
- stale detection 必须校验 `active.json` 与 `pid` 是否一致，并在 bridge 启动或 `status` 查询时做状态修正

第一版建议把超时阈值配置成显式 worker-local background control 参数，而不是隐含常量：

- `start_timeout_seconds`
- `stop_grace_period_seconds`
- `stop_force_kill_timeout_seconds`

默认值可以在实现时提供，但 contract 层必须先固定这些字段的存在性和含义，避免后续变成行为漂移的隐藏常量。

建议的 stale detection 规则：

- 若 `active.json` 记录 `starting` / `running` / `stopping`，但 pid 不存在或目标进程已死亡，则状态修正为：
  - `stopping` -> `stopped`（若 stop 由 bridge 发起且进程已退出）
  - 其余 -> `failed`，reason=`stale_process_state`
- bridge 启动时必须执行一次 cleanup-on-startup reconciliation
- `lock` 不应只靠残留文件判定活跃性，必须结合 pid 与当前进程存在性判断

### 2. Worker HTTP Bridge

bridge 作为 `tdxquant bridge serve` 常驻运行，不单独拆包。

职责：

- 接受 Master HTTP 请求
- 做 token 校验和 source allowlist
- 调用 worker 本地后台控制层
- 返回稳定 JSON result

bridge 不直接重新定义 `subscription-watch` 的业务语义，只包装控制语义。

bridge 自身的运维语义也要固定：

- 推荐部署方式：systemd / Windows Service wrapper / supervisor 之类的外部守护器
- 第一版不做自带 daemonize
- bridge 收到 SIGTERM 时默认**不主动终止活跃 watch**
- bridge 退出后，active watch 可以继续运行；bridge 重启后通过本地后台控制层重新接管状态
- bridge 自身日志与 `subscription-watch` 任务日志必须分离

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

第一版只暴露 8 个 endpoint。

- `POST /bridge/v1/watch/start`
- `POST /bridge/v1/watch/stop`
- `GET /bridge/v1/watch/status`
- `GET /bridge/v1/watch/list`
- `GET /bridge/v1/watch/artifacts`
- `GET /bridge/v1/watch/events`
- `GET /bridge/v1/watch/logs`
- `GET /bridge/v1/health`

所有 endpoint 统一使用同一层响应 envelope：

```json
{
  "ok": true,
  "result": {},
  "error": null,
  "meta": {
    "bridge_version": "v1",
    "worker_id": "worker-sh-01",
    "request_id": "..."
  }
}
```

字段要求：

- `ok`：required，布尔值
- `result`：required；成功时为对象，失败时为 `null`
- `error`：required；成功时为 `null`，失败时为对象
- `meta`：required，对象
- `meta.bridge_version`：required
- `meta.worker_id`：required
- `meta.request_id`：required

第一版不要求所有 endpoint 的 `result` payload 形状完全一致，但必须保证 envelope 四个顶层字段始终存在。

版本策略固定为 URL prefix：

- `v1` 使用 `/bridge/v1/...`
- 后续 breaking change 通过新 prefix（如 `/bridge/v2/...`）引入
- 第一版不做 header-based version negotiation

失败时：

```json
{
  "ok": false,
  "result": null,
  "error": {
    "code": "ALREADY_RUNNING",
    "message": "subscription watch is already active",
    "details": {}
  },
  "meta": {
    "bridge_version": "v1",
    "worker_id": "worker-sh-01",
    "request_id": "..."
  }
}
```

错误码第一版固定使用大写稳定命名空间，例如：

- `ALREADY_RUNNING`
- `NOT_RUNNING`
- `INVALID_REQUEST`
- `UNAUTHORIZED`
- `FORBIDDEN_SOURCE`
- `WORKER_UNHEALTHY`
- `START_FAILED`
- `STOP_FAILED`

### `POST /bridge/v1/watch/start`

输入：

- `stock_list`
- `max_events`
- `max_seconds`
- `poll_interval`
- 可选 `run_root_dir`
- 可选 `idempotency_key`

返回：

- 成功：`started`
- 若相同 `idempotency_key` 已成功启动当前 active run，则返回相同 `run_id` 与当前 active task 信息
- 若存在其他活跃任务且不匹配当前幂等键，则稳定失败 `ALREADY_RUNNING`

原因：

- Master 超时重试时，需要区分“请求未执行”和“上一次已成功启动”

### `POST /bridge/v1/watch/stop`

输入：

- 可选 `reason`
- 预留 `grace_period_seconds`

返回：

- 成功停止：`stopped`
- 没有活跃任务：建议 `noop`

虽然第一版可先使用默认优雅停止窗口，但请求 contract 应预留该字段，避免后续 breaking change。

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

但为满足 Master 远程排障，第一版应额外支持 tail 级诊断读取，而不是只返回路径：

### `GET /bridge/v1/watch/events`

输入：

- 可选 `tail`

返回：

- 当前 active 或最近一次任务的 `events.jsonl` 最后 N 条 normalized rows

### `GET /bridge/v1/watch/logs`

输入：

- 可选 `tail`

返回：

- bridge 自身日志或 worker-local watch runner 日志的最后 N 行文本/结构化日志摘要

说明：

- 这不等价于完整 artifact 文件下载
- 第一版仍然不提供通用文件代理能力

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
- 默认显式标注为 plaintext HTTP，无 TLS
- `bind_host` 需要显式配置；若用于远程控制，不允许默认绑定 `127.0.0.1`

这比用户系统、角色系统、双向 TLS 或 OAuth 简单得多，适合固定局域网环境。

限制：

- 这是“受控局域网最低可用安全边界”，不是面向公网的安全模型
- 第一版不解决 token 轮换、细粒度权限和多租户问题
- 如果网络环境不是隔离管理网，明文 Bearer token 存在被嗅探风险；这属于第一版显式 trade-off

allowlist 第一版建议按源 IP 实现，不依赖 `X-Forwarded-For` 这类可伪造头部。

## Control and Artifact Semantics

Master 应把 bridge 返回的内容视为控制结果，不直接假定 worker 本地文件布局。

关键原则：

- canonical run artifact 仍然由 worker 本地 `subscription-watch` contract 定义
- bridge 只暴露可消费的路径和摘要
- Master 不通过共享文件系统直接读 worker 文件

因此，第一版“查看 artifacts”本质上是：

- 先拿到路径和元数据
- 再通过 `events/logs tail` 进行远程快速诊断
- 完整文件代理下载或集中同步留到后续能力

## Failure Model

需要优先稳定以下失败类型：

- `ALREADY_RUNNING`
- `NOT_RUNNING`
- `INVALID_REQUEST`
- `UNAUTHORIZED`
- `FORBIDDEN_SOURCE`
- `WORKER_UNHEALTHY`
- `START_FAILED`
- `STOP_FAILED`

并发控制语义也要明确：

- `start` / `stop` 属于 control ops，第一版必须串行化处理
- 同一 worker 上的 control ops 不允许并发修改 `active.json` / `pid` / `lock`
- `status` / `list` / `artifacts` / `events` / `logs` 可以是只读并发，但读取时必须基于已提交的状态快照
- 若 bridge 使用 async HTTP server，也必须在 control ops 上加单 worker 互斥锁

其中：

- `status` 不应因为“当前没有 active task”就报 transport failure
- `list` 也不应因为“没有历史任务”就失败

第一版建议加简单 control-op debounce / rate-limit：

- 对相同来源在短窗口内重复 `start/stop` 请求做基本防抖
- 目标不是 DoS 防御，而是避免 Master 或脚本重试把 worker 控制层打乱

## Configuration

第一版需要把配置格式显式写死，避免实现期各自发明。

建议：

- Master worker registry：JSON
- Worker bridge config：JSON

原因：

- 当前仓库的运行时配置已经大量使用 JSON
- 第一版追求最小实现面，不额外引入配置解析分支

建议字段：

### Worker bridge config

- `worker_id`
- `bind_host`
- `port`
- `token`
- `master_allowlist`
- `run_root_dir`
- `log_dir`
- `start_timeout_seconds`
- `stop_grace_period_seconds`
- `stop_force_kill_timeout_seconds`

### Master worker registry

- `worker_id`
- `label`
- `host`
- `port`
- `token_env`
- `role_tags`
- `enabled`

token 第一版建议优先从环境变量注入；若支持文件，也应通过显式 `token_file` 路径引用，而不是把 secret 混在普通 registry 里。

路径约定建议显式化，而不是依赖隐藏默认值：

- worker bridge：`tdxquant bridge serve --config /abs/path/worker-bridge.json`
- Master registry consumer：`--registry /abs/path/master-workers.json`

若需要仓库内推荐位置，第一版可约定：

- worker bridge config：`runtime/bridge/worker-bridge.json`
- Master worker registry：`runtime/bridge/master-workers.json`

配置更新策略：

- 第一版不做热加载
- bridge 重启时重新读取配置
- Master 侧 worker registry 也按显式重载或进程重启生效

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
