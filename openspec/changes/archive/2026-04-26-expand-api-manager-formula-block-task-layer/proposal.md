## Why

`TdxApiManager` 的 MVP 已经把 `market` 和 `meta` 两个查询域收进了统一管理层，但当前体系仍然存在两个明显空档：

- `formula` 能力还停留在 `bridge.py + 扁平 CLI`，没有进入新的 manager 结构。
- `send_user_block` 及其代表的 `block` 写操作仍停留在旧入口，没有形成正式业务域。

与此同时，日常调用仍然需要频繁拼接多个原子 API 命令。对于研究复盘、板块扫描、自选批量刷新、缓存运维这类固定流程，当前只有原子接口，没有更稳定的场景入口。

现在需要进入 API 管理体系的第二阶段：

- 把 `formula / block` 并入新的 manager 层，补齐 API 业务域分层。
- 设计 `task` 层，给日常调用提供稳定、场景化、可复用的顶层入口。

这次 change 仍然只覆盖 API/查询侧，不涉及桌面自动化交易 capability。

## What Changes

- 扩展 `tdx-api-management` capability，使其正式覆盖 `formula` 和 `block` 两个业务域。
- 扩展 `tdx-api-cli-entry` capability，使新的 `api` 二级命令可逐步承接 `formula` / `block` 能力。
- 新增 `tdx-task-management` capability，定义 task 层作为 manager 之上的稳定场景编排入口。
- 明确 `task` 层与 `TdxApiManager` 的关系：
  - task 层只做场景编排
  - manager 层只做原子能力治理
- 明确第二阶段边界：
  - 不把桌面自动化交易并入 task 层默认实现
  - 不在本次 change 中直接重构所有旧命令
  - 先聚焦 API 侧稳定日常入口

## Capabilities

### Modified Capabilities

- `tdx-api-management`: 从 `market/meta` 扩展到 `market/meta/formula/block`
- `tdx-api-cli-entry`: 从 MVP 的只读查询入口扩展到支持 `formula / block` 的新入口规划

### New Capabilities

- `tdx-task-management`: 定义 task 层能力和稳定日常调用入口

## Impact

- 为后续代码实现新增 `formula.py`、`block.py`、`tasks/` 或等价模块提供 OpenSpec 依据。
- 为 `TdxApiManager` 向完整 API manager 演进提供明确路线，而不是继续停留在 MVP 范围。
- 为未来 `tdxquant cli task ...` 的场景化入口提供规格落点。
- 保留旧公式命令、旧板块命令与旧 CLI 兼容，不要求本次立即废弃旧入口。
