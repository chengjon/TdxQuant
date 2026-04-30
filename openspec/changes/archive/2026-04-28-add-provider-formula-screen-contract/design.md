## Context

TdxQuant 现在已经完成了 provider result envelope 和 capability discovery 两层基础设施，下一条最自然的主线就是把 `formula` 收口成第一条正式 provider business contract。两个上层项目都把 `formula` 视为 TdxQuant 最有差异化价值的能力，但它们需要的是“稳定股票列表 contract”，而不是 TongDaXin 原始公式输出的自由形状。

当前公式路径里已经有几种不同层次的能力：

- `formula_xg`: 单个已加载数据上下文里的条件选股
- `formula_process_mul_xg`: 批量选股公式执行
- `task.formula_scan`: 任务层包装，但它不是正式 provider contract

目前最接近上层需求的是 `formula_process_mul_xg`，因为它天然处理多个 symbol，并且能返回日期和值序列。但它的原始返回结构更偏向 TongDaXin 内部表现形式，例如：

- 顶层按 `symbol -> field_name -> [{Date, Value}]` 组织
- 业务侧需要自己判断 `1/0`、提取命中日期、整理 watchlist

现有约束也很清楚：

- 不能把 `task.formula_scan` 直接当成正式 provider contract
- 不能把旧 `formula-mul-xg` 的原始返回直接改写成新 schema，否则会破坏兼容
- 不能只返回“命中股票列表”，否则会丢掉上层未来需要的日期与序列信息

## Goals / Non-Goals

**Goals:**

- 定义稳定的 `formula.screen` provider contract
- 新增显式正式入口，而不是破坏旧 raw formula 入口
- 为上层系统提供标准化 `matched_symbols / unmatched_symbols / rows / summary`
- 保留按 symbol 和公式字段的基础序列细节，支持后续 watchlist/block 同步和诊断
- 让 manager、CLI 和 provider result envelope 对齐到同一能力名

**Non-Goals:**

- 不替换或删除现有 `formula-xg` / `formula-mul-xg`
- 不定义 block 写入或 watchlist 同步动作
- 不处理 `formula.zb` 指标 contract
- 不引入 HTTP 服务层
- 不在本包中做 replay/fake fixture 全覆盖

## Decisions

### 1. `formula.screen` 基于 `formula_process_mul_xg` 包装，而不是重解释 `formula_xg`

稳定 contract 将基于 `formula_process_mul_xg` 封装，因为它已经具备：

- 多 symbol 批量执行
- 时间维度结果
- 原始 `1/0` 序列

而 `formula_xg` 更适合单个预加载上下文内的原子调用，不适合作为“上层 watchlist contract”的主入口。

备选方案：

- 直接以 `formula_xg` 为正式 contract  
  否决原因：缺少批量股票列表语义，需要额外外层循环和数据准备。

### 2. 新 contract 采用新增入口，不重写旧 raw 输出

新增：

- `manager.formula.screen(...)`
- `api formula-screen`
- `tdx-formula-screen`

旧入口：

- `formula-mul-xg`
- `process_mul_xg(...)`

保持原样。

理由：

- 旧入口可能已经被手工脚本或调试流程使用
- 新 contract 可以从第一天起保持清晰 schema，不背兼容包袱

备选方案：

- 直接把 `formula-mul-xg` 改成稳定 schema  
  否决原因：会引入不必要的 breaking change。

### 3. 新 payload 同时提供摘要列表和逐 symbol 细节

`formula.screen` 的稳定 `data` 需要至少覆盖：

- `input`
- `summary`
- `matched_symbols`
- `unmatched_symbols`
- `rows`

其中每个 `row` 至少表达：

- `symbol`
- `matched`
- `field_names`
- `matched_dates`
- `latest_match_date`
- `series`

`series` 再保留 TongDaXin 公式字段及其 points 序列，这样既能让上层快速拿股票列表，也不会丢掉进一步分析所需的日期和值信息。

备选方案：

- 只返回 `matched_symbols`  
  否决原因：信息太少，不足以支持调试、回放和进一步业务判断。

### 4. 匹配语义通过固定 truthy 规则归一化

对原始公式点位值，第一版使用固定 truthy 规则判断是否命中：

- `1`
- `1.0`
- `"1"`
- `True`

其余值视为未命中。

理由：

- 文档已经说明条件选股和专家选股现在主要返回 `1/0`
- 先把最明确的规则收口，后续如出现更多变体再扩展

备选方案：

- 直接透传原值，不给 matched 语义  
  否决原因：上层还得重复做一遍核心判断，不符合 stable contract 目标。

### 5. 正式 capability name 固定为 `formula.screen`

这包新增的正式能力名固定为 `formula.screen`，而不是：

- `api.formula-screen`
- `bridge.formula-screen`
- `formula.process_mul_xg`

CLI 只是 transport 入口，不应成为正式 capability identity。

理由：

- 上层系统需要稳定业务能力名
- 这也和 provider result contract 示例中的 `formula.screen` 对齐

备选方案：

- 继续让 capability 跟 CLI route 绑定  
  否决原因：会把 transport 命名泄露进正式 contract。

## Risks / Trade-offs

- [原始公式返回 shape 可能存在更多变体] → 第一版先覆盖文档已说明的 `symbol -> field -> [{Date, Value}]` 结构，并在失败时返回清晰的 invalid/execution diagnostics。
- [新旧两套公式入口同时存在会增加认知成本] → 在文档中明确 `formula-screen` 是稳定 provider contract，`formula-mul-xg` 是原始/桥接入口。
- [matched 语义过早固化] → 先只固化最基本 truthy 规则，并保留原始序列值在 `series.points.value` 中。
- [CLI capability 命名与现有其他命令不完全一致] → 仅对新 formal contract 显式使用 canonical capability name，避免扩大旧 contract 兼容面。

## Migration Plan

1. 通过 OpenSpec 固定 `formula.screen` requirement 与 CLI/manager 增量。
2. 先补桥接、manager、CLI 的 contract 测试。
3. 实现 raw formula result 到 stable screen payload 的 normalization helper。
4. 接通 manager 和 CLI 正式入口。
5. 文档中把 `formula-screen` 标注为上层正式优先入口。

## Open Questions

- `formula.screen` 后续是否要直接支持“输出 block/watchlist mutation plan”，还是继续保持纯只读 provider contract。
