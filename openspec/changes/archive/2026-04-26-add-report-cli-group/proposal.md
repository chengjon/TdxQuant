## Why

当前报表相关能力已经比较完整，但调用入口都挂在 `task` 组下，日常使用时仍然需要记住较长的 task 子命令名称。对于明显属于“查询/复盘”的能力，更适合提供一个独立的 `report` 命令组，降低命令心智成本。

现在需要把这些稳定报表能力整理成单独的 CLI 入口层，而不是继续把所有日常操作都堆在 `task` 命令树下。

## What Changes

- 为 CLI 增加独立的 `report` 命令组。
- 在 `report` 组下暴露 `ledger`、`daily`、`period`、`lookup` 四类稳定子命令。
- 每个子命令默认绑定对应的 task profile，减少日常命令长度。
- 保留现有 `task` 下的兼容入口不变。

## Capabilities

### New Capabilities

- `tdx-report-cli-entry`: 提供面向日常复盘与查询的独立 `report` CLI 命令组

### Modified Capabilities

- `tdx-task-management`: 既有报表类 task 继续作为实现底座，被新的 `report` CLI 入口复用

## Impact

- 影响 `tdxquant/cli.py`、CLI 测试、使用文档和 CLI 入口规范。
- 不新增底层报表业务逻辑，只增加更稳定的用户入口层。
