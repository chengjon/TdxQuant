## Overview

本 change 继续补齐 `trade_audit` 的 status-oriented 日常入口矩阵，不新增新的 manager/task/report 代码路径。

目标是把当前已经稳定存在的 status filter 能力，再收口成更完整的默认入口层，覆盖：

- `confirmed` 的 period 视角
- `replayed` 的 daily / period 视角
- 围绕 confirmed / replayed 的最小 review bundle

## Design Decisions

### 1. 仍然只加配置，不加新逻辑

当前 `report` preset 解析和 `catalog` 分发逻辑已经足够稳定，也已经支持：

- `audit-daily`
- `audit-period`
- `status` filter

因此本包继续只补 runtime 配置和文档，不新增代码分支。

### 2. 先补稳定 status matrix，而不是扩完整状态全集

当前代码和测试里已经稳定出现并被聚合逻辑显式识别的状态包括：

- `confirmed`
- `replayed`
- `rejected`
- `failed`

本包先补三项最自然且已有稳定语义的缺口：

- `audit-period-confirmed`
- `audit-daily-replayed`
- `audit-period-replayed`

`failed` 先不进入 preset 矩阵，避免在缺少真实日常使用入口前过早放大。

### 3. bundle 保持最小 review 视角

本包只新增两条最小 bundle：

- `audit-confirmed-review`
  - `daily-success`
  - `audit-daily-confirmed`
- `audit-replay-review`
  - `recent-ledger`
  - `audit-daily-replayed`

这样分别覆盖：

- 成功成交后的当日复盘
- replay 视角下的轻量回看

### 4. 不引入新的执行边界

本包不会新增：

- 新的 trade/task workflow
- 自动触发交易副作用的 bundle
- 任何跨 `trade_audit` / ledger / provider` 的组合聚合逻辑

## Out of Scope

- 新增 manager/task/report workflow
- `failed` status 的 preset 矩阵
- 更复杂的跨来源联表复盘
- 自动交易类 follow-up workflow
