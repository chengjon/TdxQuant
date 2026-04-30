## Why

`report` 命令组已经把报表查询从 `task` 树里单独整理出来，但日常使用时仍然要重复输入一批稳定参数，例如 `timezone`、`trade_ok`、`recent_limit`、导出路径和默认 profile。现在需要再补一层“可命名的快捷调用模板”，把这些高频组合固化成更短的日常命令。

## What Changes

- 为 `report` 命令组增加可配置的 preset 机制。
- 新增 preset 列表查询入口，便于查看当前可用的快捷命令。
- 新增 preset 执行入口，把 preset 解析后的参数复用到既有 `report` workflow。
- 增加独立的 runtime 配置文件，承载可维护的 report preset 定义。
- 保持现有 `report ledger|daily|period|lookup` 与 `task` 兼容入口不变。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-report-cli-entry`: 为既有 `report` CLI 入口增加 preset 列表与 preset 执行能力

## Impact

- 影响 `tdxquant/cli.py`、CLI 测试、runtime 配置与使用文档。
- 新增 runtime 报表 preset 配置解析逻辑。
- 不新增新的报表 manager 或 task workflow，只扩展 CLI 入口层。
