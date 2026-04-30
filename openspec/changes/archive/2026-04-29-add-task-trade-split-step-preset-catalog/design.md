## Overview

本 change 只做 split-step 桌面交易 workflow 的日常入口收口，不新增新的 trade 或 task 代码路径。

目标是让调用方可以像使用既有：

- `guarded-default`
- `task-buy-default`
- `submit-once-default`
- `task-buy`
- `task-submit-once`

一样，直接通过：

- task preset
- command catalog entry
- 最小 follow-up bundle

来消费已经稳定的 split-step 交易 workflow。

## Design Decisions

### 1. 只加配置，不加新逻辑

当前 `task` preset 解析和 `catalog` 分发逻辑已经足够稳定，也已经支持：

- `trade-submit-ready`
- `trade-confirm-current`

因此本包只补 runtime 配置和文档，不再新增代码分支。

### 2. preset 名称沿用现有 task 风格

沿用当前 task preset 命名习惯：

- `submit-ready-default`
- `confirm-current-default`

这样可以与现有：

- `guarded-default`
- `task-buy-default`
- `submit-once-default`

形成可预测对照。

### 3. catalog entry 与 workflow 命名直接对齐

catalog entry 采用：

- `task-submit-ready`
- `task-confirm-current`

这样既与现有：

- `task-buy`
- `task-submit-once`

保持一致，也能明确表明它们来自 `task` 命令组，而不是 `trade` 直连命令组。

### 4. bundle 只覆盖 confirm 后续，不自动跨越 submit-ready 边界

split-step 的价值在于把“推进到确认框”和“真正确认”分开。因此本包不会增加一个自动串联：

- `task-submit-ready`
- `task-confirm-current`

的 bundle，避免弱化手动边界。

最小 bundle 只覆盖 confirm 之后的固定 follow-up：

- `task-confirm-current`
- `audit-daily-review`

推荐 bundle 名：

- `confirm-audit-review`

## Out of Scope

- 新增 trade 或 task workflow
- 修改 split-step 的底层副作用边界
- 自动串联 `submit-ready -> confirm-current`
- 更复杂的 split-step 交易 bundle 矩阵
