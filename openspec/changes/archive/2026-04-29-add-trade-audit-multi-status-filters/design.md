## Overview

本 change 把 `trade_audit` 从“单状态过滤”扩到“多状态 OR 过滤”，并以异常复盘入口作为第一批稳定消费面。

目标是让调用方可以直接表达：

- `rejected + failed`
- 未来其他多状态组合

而不是手工执行多次查询再拼接结果。

## Design Decisions

### 1. 保留单状态，增量补多状态

现有：

- `status: str | None`

语义已经稳定，本包不改掉它，只增量补：

- `statuses: list[str] | None`

并约定：

- `status` 与 `statuses` 不能同时使用
- `statuses` 采用 OR 语义

### 2. CLI 使用独立参数，不重载单值参数

为避免破坏现有调用，本包不会把 `--status` 改成可重复，而是新增：

- `--status-any`

它可重复传入，最终映射到：

- `statuses: list[str]`

### 3. 第一批 preset 只做异常组合

多状态能力第一批只落最自然的异常视角：

- `audit-daily-exceptions`
- `audit-period-exceptions`

它们固定映射：

- `statuses = ["rejected", "failed"]`

### 4. bundle 保持最小诊断形态

本包只新增一个最小 bundle：

- `audit-exception-diagnostics`
  - `recent-failures`
  - `audit-daily-exceptions`

这样同时保留：

- task ledger 的失败视角
- immutable `trade_audit` 的异常组合视角

## Out of Scope

- 任意复杂布尔过滤
- `trade_audit lookup` 的多状态扩展
- 跨 `trade_audit` / task ledger / submission ledger` 联表聚合
- 更多异常组合矩阵
