## Context

当前查询主线中的 `runtime` 子域，所有入口都经由 `tdxquant/api/bridge.py` 的 `_run_tq_call(...)` 统一执行。这条路径会在每次调用时执行：

1. `tq.initialize(...)`
2. 调用单个官方方法
3. `tq.close()`

这个模式适合 `get_trading_dates`、`refresh_kline`、`download_file`、`send_warn` 这类一次性动作，但不适合 `subscribe_hq / unsubscribe_hq / get_subscribe_hq_stock_list`。官方文档明确要求订阅回调依赖“策略需要正在运行”，而且订阅列表属于当前策略运行上下文。如果继续沿 one-shot wrapper 增加三个同步函数，就会得到一个调用后立即销毁的伪 session，语义错误。

同时，CLI 当前也是 one-shot 进程模型，天然不具备承载 Python 回调与持久会话的能力。因此本次设计重点不是再补三个命令名，而是先在 Python API 管理层引入可复用的持久 session 基础设施。

## Goals / Non-Goals

**Goals:**

- 在 `bridge` 层新增一个持久 runtime 订阅 session 抽象，负责单次初始化、多次调用、显式关闭。
- 在 `runtime` 子域和 `TdxApiManager.runtime` 上暴露 session 打开入口。
- 在 session 内标准化收口：
  - `subscribe_hq`
  - `unsubscribe_hq`
  - `get_subscribe_hq_stock_list`
- 保持订阅 stock list 与 callback 显式传入，不从 profile 解析默认订阅对象。
- 为后续 task 层、长驻进程或守护进程式 CLI 复用这层 session 打基础。

**Non-Goals:**

- 不在本次为 `tdxquant/cli.py` 增加 one-shot 订阅命令。
- 不在本次实现跨进程 session registry、后台 daemon、IPC 或 WebSocket 推送。
- 不在本次设计通用事件持久化、重连、断点恢复或回放机制。
- 不改动桌面交易 capability、task 报表链路或已有 one-shot runtime 命令。

## Decisions

### 1. 引入独立的持久订阅 session，而不是复用 `_run_tq_call(...)`

决策：

- 在 `tdxquant/api/bridge.py` 中新增专用 session 抽象，例如 `TdxRuntimeSubscriptionSession`。
- 该对象负责：
  - 初始化 `tqcenter`
  - 保持底层 `tq` 运行态
  - 提供 `subscribe_hq(...)`、`unsubscribe_hq(...)`、`get_subscribe_hq_stock_list()`、`close()`
  - 维护 `closed` 状态并实现 `__enter__ / __exit__`

原因：

- 订阅能力的核心约束就是“同一运行会话内的多次调用”，而 `_run_tq_call(...)` 的职责是“一次性调用后关闭”。
- 把订阅语义放入单独对象，比在 `_run_tq_call(...)` 上加布尔开关更清晰，也能避免影响已稳定的一次性 runtime 能力。

备选方案：

- 为 `_run_tq_call(...)` 增加 `keep_alive=True`
  - 放弃，原因是它会把一次性路径和持久会话路径混在同一控制流里，后续更难维护。

### 2. `manager.runtime` 仅暴露“打开 session”的入口，不直接增加 one-shot 订阅方法

决策：

- 在 `RuntimeApi` 和 `TdxApiManager.runtime` 上增加 `open_subscription_session(...)`。
- 该入口返回一个 manager-aware session 对象。
- 真正的 `subscribe_hq / unsubscribe_hq / get_subscribe_hq_stock_list` 放在 session 对象上，而不是直接挂成 `manager.runtime.subscribe_hq(...)` 这类 one-shot 方法。

原因：

- 订阅治理的本质是生命周期管理，必须让调用方显式拥有“我现在持有一个活着的会话”这个概念。
- 如果直接把订阅函数挂成 one-shot manager 方法，会再次把错误模型包装成看起来和 `send_warn` 一样的同步调用。

备选方案：

- 在 `manager.runtime` 上增加 `subscribe_hq(...)`、`unsubscribe_hq(...)`、`get_subscribe_hq_stock_list(...)`
  - 放弃，原因是这会掩盖会话存在，导致 API 表面简单但语义错误。
- 通过 session_id 在 manager 内维护全局注册表
  - 暂不采用，原因是当前只需要同进程内 Python 复用，会话对象本身更直接、更易测试。

### 3. 保持回调签名与官方接口兼容，不在本次做高层事件模型改造

决策：

- session 的 `subscribe_hq(...)` 继续接受显式 Python callback。
- callback 按官方接口的原始更新载荷语义透传，不在本次强制改成新的事件类或统一 JSON 模型。

原因：

- 官方接口本身就是 callback 驱动，本次目标是先把生命周期模型摆正，而不是再引入一层新的事件抽象。
- 这样后续 task 层如果需要 JSONL、CSV 或消息队列落盘，可以在 session 之上额外包装，而不是反向污染底层 runtime 能力。

备选方案：

- 在本次直接引入统一事件对象或文件 sink
  - 放弃，原因是会扩大范围，并把“持久 session”与“事件消费策略”耦合在一起。

### 4. 本次明确不补 CLI 订阅命令

决策：

- 本 change 不修改 `tdxquant/cli.py` 的订阅命令面。
- 如果未来需要 CLI 侧订阅能力，应单独设计为：
  - 长驻 task 命令
  - 或后台守护进程 + 控制命令
  - 或明确的事件落盘会话命令

原因：

- 当前 CLI 是 one-shot 进程，退出后会直接丢失 session。
- CLI 也无法直接接受 Python callback，因此即使补出 `api subscribe-hq` 命令名，也不能正确表达官方行为。

备选方案：

- 强行新增 `api subscribe-hq`
  - 放弃，原因是它会制造“命令成功但订阅并未持续存在”的错误预期。

### 5. session 方法继续返回 `Result`，并附带 manager metadata / timing / session_id

决策：

- `open_subscription_session(...)` 返回 session 对象本身。
- session 上的业务方法返回 `Result`。
- manager-aware session 在返回值中继续附带：
  - `domain=runtime`
  - 方法名
  - timing
  - `session_id`
  - strategy path / profile 上下文

原因：

- 这样既保留了“会话对象”这一必要抽象，又不打破当前 manager 结果封装风格。
- `session_id` 可用于日志、调试和未来 task/daemon 层复用。

## Risks / Trade-offs

- [Python API 与 CLI 能力暂时不对称] → 这是刻意范围控制；先把正确的会话层落地，再让 task/daemon 复用。
- [会话对象引入新的资源释放责任] → 通过 `close()` 与上下文管理器约束调用方式，并在 use-after-close 时返回结构化错误。
- [callback 仍沿官方原始语义，用户体验不够“高级”] → 这是本次的保守选择；高层事件标准化留给后续 task 层。
- [需要新的测试方式验证生命周期] → 通过 mock `tqcenter` 与 fake callback 做单元测试，避免依赖真实 TongDaXin 运行环境。

## Migration Plan

1. 在 `bridge.py` 中引入新的持久订阅 session 抽象，不改动现有 `_run_tq_call(...)` 行为。
2. 在 `runtime.py` 与 `manager.py` 中增加 `open_subscription_session(...)` 和 manager-aware session 包装。
3. 为 session 生命周期、订阅代理、关闭语义和 metadata 增加测试。
4. 更新覆盖矩阵与系统方案文档，把剩余订阅缺口从“未设计”切换为“已有持久 session 路线”。

回滚策略：

- 该 change 与现有 one-shot runtime 能力解耦，若实现不稳定，可整体回退 session 新入口，不影响既有查询与 `send_warn`。

## Open Questions

- 后续 task / CLI 侧是更适合做“前台长驻命令”，还是“后台守护进程 + 控制命令”？
- 是否需要在下一包为 callback 异常记录统一 warnings / telemetry？
- 是否要在后续把 session 能力推广给其他潜在需要持久上下文的 runtime 接口？
