## Context

当前 catalog 已支持：

- `list`
- `run --entry`
- `run --bundle`
- bundle 局部 step 选择

但仍缺少“只解析不执行”的命令入口。

## Goals / Non-Goals

**Goals:**

- 提供统一的 `catalog plan` 命令。
- 对 entry 和 bundle 都能返回结构化计划结果。
- 计划结果要体现显式 CLI 参数覆盖后的最终解析状态。
- 保证 plan 不触发任何底层 workflow。

**Non-Goals:**

- 不生成 shell 命令字符串。
- 不校验底层业务能否成功执行，只做入口层解析。
- 不做跨 step 数据流推导。

## Decisions

### 1. 使用独立 `catalog plan`，而不是给 `run` 再塞一个预览开关

计划和执行是两个不同动作。单独子命令更清晰：

- `catalog run ...`
- `catalog plan ...`

这样不会把执行命令越塞越复杂，也避免误触发真实 workflow。

### 2. plan 复用现有 namespace 构造与 preset 解析逻辑

对单条 entry：

1. 解析 entry -> `source` + `preset`
2. 构造下游 namespace
3. 调用对应 preset namespace builder
4. 输出解析结果，不调用实际 handler

对 bundle：

1. 解析 bundle 和 step 选择范围
2. 对每个选中 step 重复上述单条 entry planning 逻辑
3. 聚合为 bundle plan

### 3. plan 结果结构化输出

entry plan 输出：

- `catalog_entry`
- `dispatch`
  - `source`
  - `preset`
  - `command_group`
  - `command_name`
- `resolved_args`

bundle plan 输出：

- `catalog_bundle`
  - 总 step 数
  - 选中范围
- `steps`
  - 每步的 entry/source/preset/command/resolved_args

### 4. plan 输出中的 `resolved_args` 只保留可 JSON 序列化字段

CLI namespace 中可能包含内部字段或 `None`。本轮约定：

- 保留普通标量、列表、字典和 `None`
- 不尝试还原复杂对象

这样输出稳定、可写入文件、适合文档和排障。

## Risks / Trade-offs

- [计划结果字段较多] → 这是为了可排障性，后续如有需要再裁剪视图。
- [plan 不代表实际成功] → 文档明确它只验证入口层解析，不验证业务执行成功。
