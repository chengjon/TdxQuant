# Worker Bridge HTTP Control Plane Design — Review

**审核对象：** `2026-05-02-worker-bridge-http-control-plane-design.md`
**审核日期：** 2026-05-02
**总体评价：** 设计方向正确，V1 边界克制合理，但存在若干语义缺口和遗漏项需要在实现前补齐。

---

## 1. 状态机不完整

第 146–152 行定义了 6 个状态（`starting` / `running` / `stopping` / `completed` / `failed` / `stopped`），但缺少：

- **状态转换表** — 没有定义哪些转换是合法的。例如 `completed` 能否直接回到 `starting`？`failed` 之后能否直接 `start`？`stopping` 超时后是变成 `failed` 还是 `stopped`？
- **超时语义** — `starting` 如果子进程一直没起来，多久后判定为 `failed`？`stopping` 如果 SIGTERM 后进程不退出，是否升级到 SIGKILL？超时阈值是什么？
- **僵尸状态** — worker 进程 crash 后 `active.json` 可能残留 `running` 状态。缺少 stale detection 机制（如 pid file + `/proc/{pid}` 校验）。

**建议：** 补充一张状态转换矩阵表，至少覆盖 happy path + 3 种常见失败路径（进程 crash、start timeout、stop timeout）。

---

## 2. HTTP Contract 缺项

### 2.1 `start` 缺少幂等设计

第 208–220 行：`POST /start` 对 `already_running` 返回稳定失败。但如果 Master 网络超时重试，它无法区分"请求到达前已在运行"和"上一次请求成功启动了"。建议：

- 返回中包含 `task_id` / `run_id`，让 Master 做幂等判断
- 或增加 `POST /watch/start?idempotency_key=xxx` 语义

### 2.2 `stop` 缺少优雅度控制

第 222–231 行：只有一个 `stop`，没有区分 graceful vs forceful。建议至少预留 `grace_period_seconds` 参数，即便 V1 不实现。

### 2.3 `artifacts` 缺少日志查看

第 253–263 行：只返回路径和摘要，但在 remote debugging 场景下，Master 最需要的是**最后 N 行日志**（stderr / events tail）。纯返回路径在 Master 和 worker 没有共享文件系统时无法消费。

建议 V1 至少支持：

- `GET /bridge/v1/watch/artifacts/events?tail=50`
- `GET /bridge/v1/watch/artifacts/logs?tail=50`

### 2.4 缺少 `GET /bridge/v1/watch/artifacts/:run_id`

当前 `artifacts` 只返回当前或最近一次。如果有历史 run 目录（completed/failed），没有按 run_id 查询的能力。V1 可不做，但应在 Non-Goals 中明确。

### 2.5 响应格式未标准化

所有 endpoint 的响应 JSON schema 没有统一定义。建议增加：

- 统一 envelope：`{"ok": true/false, "result": {...}, "error": {...}}`
- 每个字段标注 required/optional
- 错误码统一命名空间（如 `ALREADY_RUNNING` vs `already_running`）

---

## 3. 并发与锁语义模糊

第 129–131 行说"单 worker 同时最多 1 个活跃后台 watch"，但没说：

- `start` 和 `stop` 并发到达时锁怎么处理？
- `lock` 文件是什么语义？advisory？进程级？bridge 进程 crash 后 lock 残留怎么清理？
- bridge 自身是否单线程？如果用 async HTTP server，同一个 worker 上的并发请求如何序列化？

**建议：** 明确 bridge 请求处理模型（建议 single-request-serialize for control ops），以及 lock file 的 cleanup-on-startup 逻辑。

---

## 4. 安全模型补充

第 275–287 行的安全边界对于 V1 局域网场景是合理的，但遗漏了：

- **TLS** — 局域网内明文 HTTP 传 Bearer token，任何同网段主机可以嗅探。如果 worker 机器不在完全隔离的管理网络，这是实际风险。建议至少在文档中标注 "plaintext HTTP, no TLS" 作为显式 trade-off。
- **bridge 绑定地址** — 应明确 `bind_host` 默认为 `0.0.0.0` 还是 `127.0.0.1`。如果前者，需要配合 source allowlist；如果后者，需要额外 proxy 才能远程访问。文档未指明。
- **rate limiting** — 没有。对 `start/stop` 这类幂等敏感操作，至少应有简单的防抖。

---

## 5. Configuration 格式未定义

第 169–180 行描述了 worker registry 的字段，但：

- 配置文件格式（YAML / TOML / JSON）未指定
- 配置文件路径约定未说明
- token 的存储方式（明文文件？环境变量？）未说明
- 是否支持热 reload 配置

---

## 6. Operational Gaps

### 6.1 bridge 进程管理

`tdxquant bridge serve` 自身作为常驻进程，它的 daemon 化方式未说明：

- systemd unit？
- screen/tmux？
- 自带 daemonize？
- 自身 pid file 管理？

### 6.2 日志

bridge 自身日志写到哪里？与 subscription-watch 的日志如何区分？

### 6.3 graceful shutdown

bridge 收到 SIGTERM 时，如果有活跃 watch 任务，是：

- 等任务完成再退出？
- 立即退出，任务继续跑？
- 主动 stop 任务再退出？

---

## 7. 小问题

- 第 35 行 "source allowlist" 在 Security Model 里说是 worker 侧，但 HTTP Contract 没有说明如何实现（IP 白名单？X-Forwarded-For 校验？）
- 第 296 行 "Master 不通过共享文件系统直接读 worker 文件" — 这是一个很好的原则，但与 artifacts 只返回路径存在矛盾：如果 Master 无法读文件，返回路径有什么用？建议 V1 至少返回 `events.jsonl` 的最后 N 条记录。
- 缺少版本策略：API 路径用了 `/bridge/v1/`，但没说 V1 到 V2 的兼容策略（是 header 协商还是 URL prefix）

---

## 建议优先补充项

| 优先级 | 项目 | 原因 |
|--------|------|------|
| P0 | 状态转换矩阵 + 僵尸检测 | 实现时必须先确定，否则 lifecycle 会出 bug |
| P0 | 并发/锁语义 | 同上 |
| P0 | bridge 进程管理和 graceful shutdown | 影响运维可靠性 |
| P1 | 统一响应 envelope + error schema | 前后端协作基础 |
| P1 | artifacts tail endpoint | 远程排障刚需 |
| P2 | TLS trade-off 显式标注 | 安全审计时需要 |
| P2 | 配置文件格式约定 | 实现细节，可后续补 |
