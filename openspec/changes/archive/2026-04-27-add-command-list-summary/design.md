## Context

当前 catalog 已支持：

- `list`
- `run`
- `plan`
- `labels`
- `summary` view for `run` / `plan`

但 `list` 仍缺少同等级的“快速浏览”视图。

## Goals / Non-Goals

**Goals:**

- 为 `catalog list` 增加 `--view detailed|summary`。
- 给 entry / bundle 列表提供稳定排序。
- summary 视图下只保留高信号发现字段。

**Non-Goals:**

- 不改变 `list` 的过滤语义。
- 不修改 runtime registry 结构。
- 不做复杂排序表达式或多字段排序开关。

## Decisions

### 1. `catalog list` 复用 `--view detailed|summary`

保持 catalog 子命令体验一致：

- `list`
- `run`
- `plan`

都支持 `--view summary`，默认仍 `detailed`。

### 2. 排序策略保持简单稳定

对 entry / bundle 列表统一采用：

1. 标签数量降序
2. 名称升序

这样：

- 标签更完整的条目更靠前
- 同级下结果稳定、可预测

### 3. list summary 只保留发现字段

entry summary：

- `name`
- `source`
- `command`
- `labels`
- `description`

bundle summary：

- `name`
- `labels`
- `step_count`
- `step_names`
- `description`

### 4. handler 负责生成 `summary_view`

延续 `run` / `plan` 的做法，在 `Result.data` 中挂：

- `summary_view`

最终 `main()` 根据 `catalog list --view summary` 切换输出。

## Risks / Trade-offs

- [排序依据主观] → 本轮只求稳定和可预测，不追求智能推荐。
- [summary 过短可能丢信息] → 默认仍是 detailed，需要时随时回到完整视图。
