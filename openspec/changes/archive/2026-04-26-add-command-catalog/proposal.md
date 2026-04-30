## Why

现在虽然已经有 `task`、`report`、`trade` 三套稳定入口和各自 preset，但日常使用仍然要先记住命令组，再记住 preset 所属位置。对于高频操作，这一层认知切换仍然偏重，不符合“给日常调用一个更稳定的顶层入口”的目标。

需要补一层统一 command catalog，把跨 `task` / `report` / `trade` 的常用 preset 收敛成一个总入口，继续降低长命令维护成本，同时避免复制现有 workflow 逻辑。

## What Changes

- 新增统一 command catalog 配置文件，用于把 `task` / `report` / `trade` preset 命名化收口。
- 新增顶层 `catalog` CLI 命令组，提供列表与执行入口。
- catalog 执行时复用既有 preset 分发链，不新增新的 manager/workflow 逻辑路径。
- 补充 catalog 使用文档与回归测试。

## Capabilities

### New Capabilities

- `tdx-command-catalog`: 提供跨 `task` / `report` / `trade` 的统一日常命令目录层

### Modified Capabilities

None.

## Impact

- 影响 `tdxquant/cli.py`、新增 catalog 解析 helper、runtime 配置、CLI 测试与使用文档。
- 不修改 `TdxTaskManager`、`TdxTradeManager`、`TdxApiManager` 的业务行为。
- 不移除现有 `task` / `report` / `trade` 原生命令和各自 preset 入口。
