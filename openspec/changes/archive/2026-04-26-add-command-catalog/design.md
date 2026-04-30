## Context

当前已经存在三套“命令级默认值”能力：

- `report preset`
- `trade preset`
- `task preset`

它们各自都稳定，也已经形成了统一的 `list + run` 模式。但从日常操作角度，用户仍然需要先判断“这次属于 report / trade / task 哪一类”，然后再进入对应命令组执行。这对高频使用场景仍然过重。

## Goals / Non-Goals

**Goals:**

- 提供单一顶层目录层，统一列出高频日常命令。
- 允许通过一个入口执行 `task` / `report` / `trade` preset。
- 保证显式 CLI 参数继续覆盖 preset 默认值。
- 保持现有命令兼容，不引入新的业务逻辑路径。

**Non-Goals:**

- 不合并三套底层 preset 文件。
- 不重写既有 `task/report/trade` 分发逻辑。
- 不把原子 `api` 查询命令纳入这轮 catalog。
- 不新增新的 manager、workflow 或 profile 体系。

## Decisions

### 1. 新增独立 catalog registry，而不是合并现有 preset 文件

本轮新增 `runtime/command-catalog.json`，每个 entry 只声明：

- `source`: `task` / `report` / `trade`
- `preset`: 对应命令组里的 preset 名称
- `description`: 可选的人类可读说明

这样 catalog 只是“统一索引层”，不会破坏现有 preset 的职责边界。

### 2. CLI 采用 `catalog list` + `catalog run --entry ...`

统一入口采用显式命令组：

- `catalog list`
- `catalog run --entry <name>`

`list` 用于发现当前稳定入口；`run` 用于执行指定 entry。这样既保持显式性，也与现有 `report/trade/task` 的 `presets/run` 结构相呼应。

### 3. catalog 执行时回落到既有 preset 分发链

catalog 不直接调用 manager 或 workflow。执行策略是：

1. 解析 catalog entry，拿到 `source` 与 `preset`
2. 构造对应命令组的运行 namespace
3. 继续调用既有：
   - `_handle_report_subcommand()`
   - `_handle_trade_subcommand()`
   - `_handle_task_subcommand()`

这样 catalog 只是“上面再包一层入口”，不会形成第四套平行业务路径。

### 4. `catalog run` 使用联合参数面，但只做透传覆盖

为了保留“显式 CLI 参数覆盖 preset 默认值”的能力，`catalog run` 会暴露一组联合参数面，覆盖：

- report 高频查询参数
- trade 高频交易参数
- task 高频 workflow 参数

这些参数本身不在 catalog 层做业务解释，只是原样传给下游命令组。对当前 entry 无意义的参数会自然被忽略。

## Risks / Trade-offs

- [参数面偏宽] → catalog 只是顶层通用入口，底层执行仍交由各命令组处理。
- [entry 名称可能冲突] → 在 `command-catalog.json` 中统一维护唯一 entry 名称。
- [catalog 与 preset 看起来接近] → 文档明确：preset 是“命令组内部模板”，catalog 是“跨命令组目录层”。
