## Overview

本 change 只做 `trade_audit` 与 split-step follow-up 的入口组合增强，不新增任何新的 manager/task/report 代码路径。

目标是补齐两个高频日常视角：

- `rejected` 审计诊断
- `confirm-current` 后的更完整 follow-up

## Design Decisions

### 1. 继续只加配置，不加逻辑

当前 `report` preset 解析和 `catalog` 分发已经足够稳定，也已经支持：

- `audit-daily`
- `audit-period`
- `task-confirm-current`

因此本包仍然只补 runtime 配置和文档，不新增代码分支。

### 2. `trade_audit` richer preset 先围绕 `rejected`

现有稳定状态口径里，`confirmed` 已经有单日 preset：

- `audit-daily-confirmed`

当前更缺的是拒单/异常诊断视角，因此本包只新增：

- `audit-daily-rejected`
- `audit-period-rejected`

不在这一包里扩成完整状态矩阵。

### 3. bundle 保持两类最小用法

本包只新增两条最小 bundle：

- `audit-rejection-diagnostics`
  - `recent-failures`
  - `audit-daily-rejected`
- `confirm-complete-review`
  - `task-confirm-current`
  - `daily-success`
  - `audit-daily-confirmed`

这样分别覆盖：

- 排障诊断路径
- 分步确认后的固定日常回看路径

### 4. 不自动串联 submit-ready 到 confirm-current

本包仍然不增加：

- `task-submit-ready`
- `task-confirm-current`

的自动串联 bundle，保持 split-step 的手动边界不被弱化。

## Out of Scope

- 新增 manager/task/report workflow
- 扩成完整 `trade_audit status` preset 矩阵
- 自动串联 `submit-ready -> confirm-current`
- 更复杂的交易复盘 bundle 编排
