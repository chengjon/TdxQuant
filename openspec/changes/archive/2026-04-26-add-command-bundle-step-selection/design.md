## Context

当前 bundle 已支持：

- 顺序执行多个既有 catalog entry
- step 级默认参数
- 失败即停止
- 聚合结果输出

缺口在于：缺少“只执行一段步骤”或“只执行某一步”的稳定控制。

## Goals / Non-Goals

**Goals:**

- 支持用 step 名称或序号选择 bundle 的执行范围。
- bundle 结果里明确记录原始 step 总数、本次选择范围、实际执行的 step。
- 保持未选择 step 完全不执行。

**Non-Goals:**

- 不支持条件跳转、动态依赖、变量传递。
- 不支持多段离散 step 选择。
- 不支持自动根据上次执行结果恢复。

## Decisions

### 1. step 增加稳定 `name`

bundle step 结构扩展：

- `name`: 可选稳定名称
- 未配置时默认取 `entry`

这样既兼容现有 bundle，又给选择执行提供稳定标识。

### 2. CLI 使用 `--from-step` / `--to-step` / `--only-step`

在 `catalog run --bundle ...` 上增加：

- `--from-step`
- `--to-step`
- `--only-step`

取值既可以是：

- step 名称
- 1-based 序号字符串，例如 `1`、`2`

约束：

- `--only-step` 与 `--from-step` / `--to-step` 互斥
- 若 `from > to`，返回 invalid-request
- 未匹配到 step 时，返回 invalid-request

### 3. 执行前先解析选择范围，再切片执行

bundle 执行流程调整为：

1. 解析完整 bundle
2. 解析 step 名称列表
3. 根据 CLI 选择参数得到 `[start_index, end_index]`
4. 只执行选中的连续 step
5. 汇总结果中保留：
   - `selected_from_step`
   - `selected_to_step`
   - `selected_step_count`
   - `executed_steps`

### 4. list 输出补充 step 名称

`catalog list --bundle ...` 结果中的每个 step 现在显式返回：

- `index`
- `name`
- `entry`

这样用户在执行前可以先查看可选 step。

## Risks / Trade-offs

- [step 名称冲突] → 单个 bundle 内要求名称唯一，默认 entry 时也按该规则校验。
- [参数变多] → 只增加三个 bundle 专用参数，仍然低于新增独立命令组的复杂度。
- [局部执行可能绕过前置条件] → 这是调用者显式选择的结果，bundle 仍不隐藏底层 workflow 的真实要求。
