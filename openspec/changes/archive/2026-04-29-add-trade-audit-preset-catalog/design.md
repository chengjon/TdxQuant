## Overview

本 change 只做 `trade_audit` 的日常入口收口，不新增新的 manager/task/report 代码路径。

目标是让调用方可以像使用既有交易日报和台账入口一样，直接通过：

- report preset
- command catalog entry
- 最小 bundle

来消费稳定 `trade_audit` report workflow。

## Design Decisions

### 1. 只加配置，不加新逻辑

当前 `report` preset 解析和 `catalog` 分发逻辑已经足够稳定，也已经支持：

- `audit-lookup`
- `audit-daily`
- `audit-period`

因此本包只补 runtime 配置和文档，不再新增代码分支。

### 2. preset 名称沿用现有 report 风格

沿用当前 report 命名习惯：

- `audit-daily-review`
- `audit-daily-confirmed`
- `audit-period-review`

这样更容易和已有：

- `daily-review`
- `daily-success`
- `period-review`

形成可预测对照。

### 3. catalog entry 与 preset 一一对应

本包的 catalog entry 不再发明新的命名层，而是直接与 report preset 同名，保持目录层与 preset 层一致。

### 4. bundle 保持最小

bundle 只补一个最小诊断入口，避免把 `trade_audit` 又拉成新的治理面。

推荐组合：

- `recent-failures`
- `audit-daily-review`

原因是它同时保留：

- 既有 task ledger 失败视角
- 新的 immutable trade audit 视角

## Out of Scope

- 新增 manager/task/report workflow
- 新增 task preset
- `trade_audit` 的跨来源联表查询
- 更复杂的 audit bundle 矩阵
