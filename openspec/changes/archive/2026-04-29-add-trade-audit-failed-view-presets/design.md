## Overview

本 change 只补 `trade_audit` 的 `failed` 视角入口，不新增新的 manager/task/report 代码路径。

目标是让 `failed` 与已经稳定的：

- `confirmed`
- `replayed`
- `rejected`

一样，拥有可直接复用的 preset 和 catalog 入口。

## Design Decisions

### 1. 继续只加配置，不加逻辑

当前 `report` preset 和 `catalog` 分发逻辑已经足够稳定，也已经支持：

- `audit-daily`
- `audit-period`
- `status` filter

因此本包继续只补 runtime 配置和文档，不新增代码分支。

### 2. `failed` 只做 daily / period + 最小诊断 bundle

本包范围收窄为：

- `audit-daily-failed`
- `audit-period-failed`
- `audit-failure-diagnostics`

避免在同一包里继续扩更多组合矩阵。

### 3. bundle 复用既有失败视角

最小 bundle 采用：

- `recent-failures`
- `audit-daily-failed`

这样可以同时保留：

- task ledger 的失败视角
- immutable `trade_audit` 的失败视角

## Out of Scope

- 新增 manager/task/report workflow
- 更复杂的 failed review 组合矩阵
- 跨 `trade_audit` / task ledger / submission ledger 的联表聚合
- 新的 split-step trade follow-up workflow
