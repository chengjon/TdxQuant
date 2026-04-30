## Why

`task` 层已经承载了稳定 workflow，但像 `guarded-trade-buy`、`trade-submit-once` 这类高频命令仍然需要重复输入端口、刷新策略、风控前置参数和导出路径。现在需要补一层 `task preset`，把这类固定 workflow 参数命名化，降低长命令维护成本。

## What Changes

- 为 `task` 命令组增加可配置的 preset 机制。
- 新增 task preset 列表入口。
- 新增 task preset 执行入口，并把 preset 参数映射回既有稳定 task workflow。
- 增加独立的 runtime task preset 配置文件。
- 保持现有 `task <subcommand>` 原生命令兼容。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-task-management`: 为稳定 task workflow 增加 preset 列表与 preset 执行能力

## Impact

- 影响 `tdxquant/cli.py`、task preset 配置解析、CLI 测试与 task 使用文档。
- 不新增新的 task manager 或 workflow 逻辑，只扩展 CLI 入口层。
