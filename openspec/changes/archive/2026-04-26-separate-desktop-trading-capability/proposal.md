## Why

当前项目已经完成两条性质不同的能力沉淀：

- 查询类能力已经通过 `TdxApiManager` 收敛到 `tdx-api-management` 体系。
- 桌面自动化交易链路已经在 `tdxquant/desktop/`、`tdxquant/brokers/` 和 `pingan-buy-submit-once` / `pingan-buy` 等命令中形成可用闭环。

但桌面自动化交易目前仍然以“命令集合 + 局部运行时逻辑 + 诊断脚本”的形态存在，尚未被正式定义为与 API 管理层并列的 capability。这会带来三个持续性问题：

- 顶层规划失衡：`api` 已有明确 capability 和 manager 边界，而交易侧仍然停留在实现细节层。
- 日常使用入口混杂：查询类能力开始走统一 manager，而交易类能力仍散落在 CLI 分支和底层模块里。
- 后续扩展困难：如果未来引入卖出、撤单、持仓读取、确认弹窗处理或 `task` 层编排，当前结构缺少清晰的能力挂载点。

现在需要把“桌面自动化交易路径”整理成独立 capability，并明确它与 `tdx-api-management` 平行存在、共享统一治理思路，但不混入同一个 manager。

## What Changes

- 新增 `tdx-desktop-trading-management` capability，定义桌面自动化交易的顶层定位、模块边界和统一入口原则。
- 新增 `tdx-desktop-trading-cli-entry` capability，定义未来 `trade` 二级命令组与现有扁平交易命令的兼容关系。
- 明确顶层并列规划：
  - `tdx-api-management` 负责只读/低风险查询治理。
  - `tdx-desktop-trading-management` 负责桌面自动化交易治理。
- 规定桌面交易能力的正式边界：
  - 保留 `tdxquant/desktop/`、`tdxquant/brokers/`、`uia_inspector`、HID/Win32/UIA 组合路线。
  - 不直接并入 `TdxApiManager`。
  - 后续如需统一顶层，也应以独立 `TradeManager` 或等价门面实现，而不是扩张现有 API manager。
- 为未来 `task` 层和场景化流程预留上层编排关系，使其可以同时调用查询 capability 与桌面交易 capability。

## Capabilities

### New Capabilities

- `tdx-desktop-trading-management`: 桌面自动化交易的独立 capability，与查询 API 管理层并列规划。
- `tdx-desktop-trading-cli-entry`: 桌面自动化交易的嵌套 CLI 入口规划，作为未来 `trade` 命令组的标准化方向。

### Modified Capabilities

- None.

## Impact

- 影响 OpenSpec 顶层规划，使项目形成至少两条正式 capability 主线：`api` 与 `desktop trading`。
- 为后续代码整理提供明确落点：`desktop` / `brokers` / 交易 CLI 命令会归入桌面交易 capability，而不是继续被视为临时实现。
- 为未来 `TradeManager`、`trade` CLI 二级命令、交易 task 层编排提供规格基础。
- 不要求本次立即重构现有交易实现，不改变当前可用命令和实盘闭环。
