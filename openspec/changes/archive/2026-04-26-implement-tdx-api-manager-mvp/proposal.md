## Why

当前项目已经接入多项 TdxQuant 查询能力，但这些能力仍然直接堆积在 `tdxquant/api/bridge.py` 和 `tdxquant/cli.py` 中，日常调用入口零散、参数冗长、后续扩展边界不清。现在需要在不打断现有桌面自动化交易链和扁平 CLI 命令的前提下，为查询类能力建立稳定的顶层管理体系。

## What Changes

- 新增查询类 API 的顶层管理门面 `TdxApiManager`，统一承接代码侧日常调用。
- 新增 `market` / `meta` 业务域模块，把已接入的查询接口按语义聚合到 manager 之下。
- 新增 API profile 配置与合并机制，支持“预设 + 显式覆盖”的日常调用模式。
- 新增 `api` 二级 CLI 入口，提供比现有扁平命令更适合日常使用的查询入口。
- 保留现有 `bridge.py`、现有扁平 CLI 命令和现有桌面自动化交易路径，不做替换或废弃。
- MVP 阶段不纳入 `send_user_block`、formula 系列和交易执行类能力，它们继续保留在旧入口中使用。

## Capabilities

### New Capabilities
- `tdx-api-management`: 定义查询类 API 的顶层管理能力，包括 `TdxApiManager`、`market` / `meta` 域封装、profile 解析与统一结果治理。
- `tdx-api-cli-entry`: 定义新的 `api` 二级 CLI 查询入口，并要求与现有扁平命令兼容共存。

### Modified Capabilities

- None.

## Impact

- 影响 `tdxquant/api/` 目录结构，新增 `context.py`、`market.py`、`meta.py`、`manager.py`。
- 影响 `tdxquant/api/__init__.py` 的公共导出策略。
- 影响 `tdxquant/cli.py`，新增 `api` 二级命令结构和独立分发逻辑。
- 新增 `runtime/api-profiles.json` 配置文件，并要求使用绝对路径解析。
- 不影响 `tdxquant/desktop/`、`tdxquant/brokers/` 现有交易自动化链路的行为。
