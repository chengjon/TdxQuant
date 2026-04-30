## Context

当前查询主线已经有独立 `runtime` 子域，并已纳入：

- `get_trading_dates`
- `refresh_kline`
- `download_file`

官方接口文档中与 runtime 更接近的剩余能力主要还有两类：

- 订阅治理：`subscribe_hq / unsubscribe_hq / get_subscribe_hq_stock_list`
- 一次性告警写入：`send_warn`

其中订阅治理要求策略进程持续运行并维持回调会话，不适合直接套进当前“一次调用即关闭”的 bridge 模型；而 `send_warn` 是一次性写入调用，可以沿现有 runtime 分层平滑纳入。

## Goals / Non-Goals

**Goals:**

- 在 `runtime` 子域中新增 `send_warn` 能力。
- 补齐 bridge、runtime domain、manager、nested CLI、flat CLI 的标准入口。
- 保持预警批次参数显式输入，不从 API profile 推断默认批次内容。
- 保留官方 `count` 语义，并允许可选列表按原样透传到底层。

**Non-Goals:**

- 不在本次处理 `subscribe_hq / unsubscribe_hq / get_subscribe_hq_stock_list`。
- 不在本次新增持久 runtime session、后台守护进程或回调治理。
- 不为预警批次做额外业务校验、去重、限流或状态落盘。
- 不改动桌面交易 capability、task/report/catalog 场景层。

## Decisions

### 1. 将 `send_warn` 归入现有 `runtime` 子域

决策：

- 在现有 `RuntimeApi` 和 `manager.runtime` 上增加：
  - `send_warn(...)`

原因：

- `send_warn` 属于运行时侧对客户端的一次性动作，不适合回到 `market/meta`。
- 与其为了单个接口新建 `signal` 域，不如先沿现有 `runtime` 边界扩展。

备选方案：

- 新建 `signal` 域
  - 放弃，原因是当前仅有 `send_warn` 一项，不足以支撑单独域。

### 2. CLI 采用语义化 `send-warn` 命名

决策：

- nested `api`
  - `api send-warn`
- flat bridge
  - `tdx-send-warn`

原因：

- 当前 CLI 已经优先采用语义化名称，而不是完全照搬官方 Python 函数名风格。
- `send-warn` 与 `download-file`、`refresh-kline` 的命名习惯一致。

### 3. CLI 使用 `--volume`，bridge 映射到官方 `volum_list`

决策：

- CLI 与 manager 使用 `volume_list` 语义。
- bridge 包装在最终调用 TdxQuant runtime 时映射为官方 `volum_list`。

原因：

- 官方参数名存在 `volum_list` 拼写，直接暴露到高层入口会降低可用性。
- 保留底层映射即可兼顾用户体验和官方接口兼容性。

### 4. 不从 profile 推断批量预警内容

决策：

- `stock_list`、`time_list`、`price_list`、`close_list`、`volume_list`、`bs_flag_list`、`warn_type_list`、`reason_list`、`count` 全部由调用方显式传入。

原因：

- 这些参数共同描述一批具体预警，不存在稳定默认值集合。
- 从 profile 推断此类列表会掩盖真实调用内容，违背 manager 收口的透明性。

## Risks / Trade-offs

- [`send_warn` 仍缺少高层批量构造器] → 这是刻意范围控制，本次只先纳入标准原子入口。
- [CLI 参数较多] → 这是官方接口固有复杂度，本次通过 repeated args 保持一一对应关系。
- [`subscribe_hq` 系列仍未覆盖] → 这是有意延期，等待单独的持久 session 方案。
