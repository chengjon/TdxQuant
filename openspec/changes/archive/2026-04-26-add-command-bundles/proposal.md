## Why

当前 `catalog` 已经解决了“单条高频命令如何统一收口”的问题，但日常使用里仍然存在一类固定的多步骤流程：

- 先刷新环境，再看最近台账
- 先执行受保护买入，再立刻查看最新摘要
- 先看当日复盘，再补一个最近台账摘要

这些流程现在仍然需要手动连续执行多条命令，和“给日常调用一个更稳定的顶层入口”的目标相比还差一层。需要在不改动既有 `task` / `report` / `trade` workflow 的前提下，再补一个可配置的多步骤 catalog bundle 入口。

## What Changes

- 新增 command bundle 配置文件，用于把多个既有 catalog entry 编排成一个命名化日常流程。
- 扩展 `catalog` CLI，使其支持列出和执行 bundle。
- bundle 执行只复用既有 catalog entry 分发链，不新增 manager 或业务 workflow 路径。
- 补充示例 bundle、使用文档与回归测试。

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`: 在统一 entry 目录层之上增加多步骤 bundle/routine 编排能力

### New Capabilities

None.

## Impact

- 影响 `tdxquant/catalog.py`、`tdxquant/cli.py`、runtime 配置、CLI/配置测试与使用文档。
- 不修改 `TdxApiManager`、`TdxTaskManager`、`TdxTradeManager` 的业务行为。
- 不替换现有 `task` / `report` / `trade` / `catalog` 单条 entry 执行路径。
