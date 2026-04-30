## Context

当前 `report` 入口已经把报表查询命令收敛成：

- `report ledger`
- `report daily`
- `report lookup`
- `report period`

但这些子命令仍然要求调用方重复输入一批稳定参数。现有 `task profile` 更偏底层 workflow 默认值，不能直接表达“给日常命令起一个稳定别名”的诉求，因此需要增加一层更接近用户操作习惯的 preset 配置。

## Goals / Non-Goals

**Goals:**

- 提供 `report` 级别的可命名 preset。
- 允许通过 CLI 查询可用 preset 列表。
- 允许通过 CLI 执行 preset，并把显式 CLI 参数覆盖到 preset 默认值之上。
- 继续复用既有 `_dispatch_report_workflow(...)` 与 `TdxTaskManager`。

**Non-Goals:**

- 不新增 `ReportManager`。
- 不修改既有报表 task 的底层统计逻辑。
- 不移除或重命名现有 `report` / `task` 命令。
- 不在本次引入复杂的日期表达式 DSL。

## Decisions

### 1. Preset 作为 CLI alias 层独立于 task profile

`task profile` 继续负责 workflow 默认行为；`report preset` 负责把一组命令参数命名化。两者职责不同，因此单独增加 `runtime/report-presets.json`，避免把用户级快捷命令和底层执行 profile 混在一起。

### 2. 新增 `report presets` 与 `report run --preset ...`

列表和执行拆成两个明确入口：

- `report presets`: 查看可用 preset
- `report run --preset <name>`: 执行 preset

这样比把 preset 做成隐式别名更可发现，也更便于后续扩展校验与说明信息。

### 3. Preset 仅解析为既有 report 子命令参数

每个 preset 只声明：

- 目标 `command`，限定在 `ledger` / `daily` / `lookup` / `period`
- 可选 `description`
- `options` 参数字典
- 可选 `profile`

执行时先解析 preset，再让显式 CLI 参数覆盖 preset 默认值，最后仍然调用统一的 `_dispatch_report_workflow(...)`。这样实现只有一条业务路径。

### 4. 显式 CLI 参数优先

如果 preset 定义了 `timezone=Asia/Shanghai`，而调用方在命令行传入 `--timezone UTC`，则以 CLI 参数为准。这是为了保证 preset 是“省输入”的工具，而不是“锁死参数”的机制。

## Risks / Trade-offs

- [配置层变多] → 通过职责拆分控制：`task profile` 管 workflow，`report preset` 管快捷命令。
- [preset 与真实能力漂移] → 通过 `report presets` 列表输出目标 command 和说明，降低黑盒感。
- [run 子命令参数面较宽] → 采用四类 report 参数并集，但执行时只消费目标 command 相关字段。
