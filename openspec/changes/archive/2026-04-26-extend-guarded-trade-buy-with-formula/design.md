## Context

`guarded_trade_buy` 已经是当前最高层的稳定交易任务模板，但还缺一块核心前置检查：公式筛选。

项目现有能力已经足够：

- `TdxTaskManager.formula_scan(...)`
- `TdxApiManager.formula.process_mul_xg(...)`

因此不需要新建新的公式执行基础设施，只需要把现有公式扫描能力纳入 guarded task。

## Goals

- 为 `guarded_trade_buy` 增加可选 formula 前置检查。
- 保持接口直观，不引入复杂规则 DSL。
- 输出仍然是单一结构化报告。

## Non-Goals

- 本次不实现多公式组合逻辑。
- 本次不实现公式结果的高级排序或评分。

## Decisions

### 1. 公式前置检查为可选约束

如果未提供 `formula_name`，则跳过公式前置检查。

如果提供：

- `formula_name`
- 可选 `formula_arg`
- 可选返回/周期参数

则在交易前对单只目标证券执行公式扫描。

### 2. 通过条件采用“单标的有命中”

对单只证券运行公式扫描后：

- 如果扫描结果中可提取到目标证券代码，或存在非空结果行
- 则视为公式条件通过
- 否则阻断交易

### 3. 报告产物记录公式前置检查

JSON 报告记录：

- 公式输入参数
- 原始公式检查结果
- 是否通过

CSV 摘要补充：

- `formula_name`
- `formula_check_passed`

## Verification

- task manager 测试验证公式前置检查通过与阻断路径。
- CLI 测试验证新参数分发。
- 回归测试验证原有 guarded task 调用不受影响。
